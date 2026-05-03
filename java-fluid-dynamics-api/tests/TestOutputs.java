import com.google.gson.*;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.MethodOrderer.OrderAnnotation;
import static org.junit.jupiter.api.Assertions.*;

import java.net.http.*;
import java.net.URI;
import java.nio.file.*;
import java.util.*;
import java.io.*;

@TestMethodOrder(OrderAnnotation.class)
public class TestOutputs {

    private static Process SERVER_PROCESS;
    private static final String BASE_URL = "http://127.0.0.1:8080";
    private static final Path SIMULATION_FILE = Path.of("/app/workspace/data/latest_simulation.json");
    private static final Path ANALYSIS_FILE   = Path.of("/app/workspace/data/latest_analysis.json");
    private static final HttpClient CLIENT = HttpClient.newHttpClient();
    private static final Gson GSON = new Gson();

    @BeforeAll
    static void setupAll() throws Exception {
        Path javaFile  = Path.of("/app/workspace/src/FluidDynamicsApi.java");
        Path pythonFile = Path.of("/app/workspace/src/postprocess.py");
        assertTrue(Files.exists(javaFile),   "FluidDynamicsApi.java is missing");
        assertTrue(Files.exists(pythonFile), "postprocess.py is missing");

        Process compile = new ProcessBuilder(
            "javac", "--add-modules", "jdk.httpserver", javaFile.toString()
        ).directory(new File("/app/workspace/src")).inheritIO().start();
        assertEquals(0, compile.waitFor(), "javac compilation failed");

        SERVER_PROCESS = new ProcessBuilder(
            "java", "--add-modules", "jdk.httpserver", "-cp", "/app/workspace/src", "FluidDynamicsApi"
        ).start();

        waitForServer();
    }

    @AfterAll
    static void teardownAll() {
        if (SERVER_PROCESS != null) SERVER_PROCESS.destroy();
    }

    static void waitForServer() throws Exception {
        HttpRequest req = HttpRequest.newBuilder().uri(URI.create(BASE_URL + "/health")).build();
        for (int i = 0; i < 30; i++) {
            try {
                HttpResponse<String> resp = CLIENT.send(req, HttpResponse.BodyHandlers.ofString());
                if (resp.statusCode() == 200) return;
            } catch (Exception e) {
                Thread.sleep(500);
            }
        }
        throw new AssertionError("Java API did not become ready on port 8080");
    }

    static JsonObject runSimulation(Map<String, Object> payload) throws Exception {
        String body = GSON.toJson(payload);
        HttpRequest req = HttpRequest.newBuilder()
            .uri(URI.create(BASE_URL + "/simulate"))
            .POST(HttpRequest.BodyPublishers.ofString(body))
            .header("Content-Type", "application/json")
            .build();
        HttpResponse<String> resp = CLIENT.send(req, HttpResponse.BodyHandlers.ofString());
        assertEquals(200, resp.statusCode(), "POST /simulate failed: " + resp.body());
        return GSON.fromJson(resp.body(), JsonObject.class);
    }

    static void assertClose(double left, double right) {
        assertTrue(
            Math.abs(left - right) <= 1e-6 * Math.max(Math.abs(left), Math.abs(right)) + 1e-6,
            left + " is not close to " + right
        );
    }

    static void assertAnalysisClose(JsonObject actual, JsonObject expected) {
        assertClose(actual.get("mean_velocity").getAsDouble(),    expected.get("mean_velocity").getAsDouble());
        assertClose(actual.get("velocity_stddev").getAsDouble(),  expected.get("velocity_stddev").getAsDouble());
        assertClose(actual.get("pressure_drop").getAsDouble(),    expected.get("pressure_drop").getAsDouble());
        assertEquals(actual.get("dominant_regime").getAsString(), expected.get("dominant_regime").getAsString());
    }

    @Test
    @Order(1)
    void test_health_and_required_files() throws Exception {
        /** Verify that the health endpoint returns status ok and both required source files exist. */
        HttpRequest req = HttpRequest.newBuilder().uri(URI.create(BASE_URL + "/health")).build();
        HttpResponse<String> resp = CLIENT.send(req, HttpResponse.BodyHandlers.ofString());
        assertEquals(200, resp.statusCode());
        JsonObject health = GSON.fromJson(resp.body(), JsonObject.class);
        assertEquals("ok", health.get("status").getAsString());
        assertTrue(Files.exists(Path.of("/app/workspace/src/FluidDynamicsApi.java")));
        assertTrue(Files.exists(Path.of("/app/workspace/src/postprocess.py")));
    }

    @Test
    @Order(2)
    void test_simulation_response_and_saved_files() throws Exception {
        /** Verify /simulate returns all required keys with correct echo values, correct array lengths,
            decreasing pressure and velocity profiles, and that both persistence files are written. */
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("viscosity", 0.12);
        payload.put("inlet_velocity", 2.4);
        payload.put("grid_points", 6);
        payload.put("steps", 4);
        JsonObject data = runSimulation(payload);

        assertEquals(
            new HashSet<>(Arrays.asList("viscosity", "inlet_velocity", "grid_points", "steps",
                "reynolds_number", "velocity_profile", "pressure_profile", "analysis")),
            data.keySet()
        );

        assertClose(data.get("viscosity").getAsDouble(),       0.12);
        assertClose(data.get("inlet_velocity").getAsDouble(),  2.4);
        assertEquals(6, data.get("grid_points").getAsInt());
        assertEquals(4, data.get("steps").getAsInt());

        JsonArray vel  = data.getAsJsonArray("velocity_profile");
        JsonArray pres = data.getAsJsonArray("pressure_profile");
        assertEquals(6, vel.size());
        assertEquals(6, pres.size());
        assertTrue(vel.get(0).getAsDouble() > vel.get(vel.size() - 1).getAsDouble(),
            "inlet velocity must exceed outlet velocity");
        for (int i = 0; i < pres.size() - 1; i++) {
            assertTrue(pres.get(i).getAsDouble() >= pres.get(i + 1).getAsDouble(),
                "pressure profile must be non-increasing");
        }

        assertTrue(Files.exists(SIMULATION_FILE), "latest_simulation.json was not written");
        assertTrue(Files.exists(ANALYSIS_FILE),   "latest_analysis.json was not written");

        JsonObject savedSim      = GSON.fromJson(Files.readString(SIMULATION_FILE), JsonObject.class);
        JsonObject savedAnalysis = GSON.fromJson(Files.readString(ANALYSIS_FILE),   JsonObject.class);
        assertEquals(6, savedSim.get("grid_points").getAsInt());
        assertEquals(data.getAsJsonArray("velocity_profile"), savedSim.getAsJsonArray("velocity_profile"));
        assertAnalysisClose(savedAnalysis, data.getAsJsonObject("analysis"));
    }

    @Test
    @Order(3)
    void test_python_postprocess_matches_api_analysis_and_latest_report() throws Exception {
        /** Verify that running postprocess.py directly reproduces the API analysis, and that
            /latest-report serves the same analysis. */
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("viscosity", 0.18);
        payload.put("inlet_velocity", 3.1);
        payload.put("grid_points", 7);
        payload.put("steps", 5);
        JsonObject data = runSimulation(payload);

        Process proc = new ProcessBuilder(
            "python3", "/app/workspace/src/postprocess.py", SIMULATION_FILE.toString()
        ).start();
        String stdout = new String(proc.getInputStream().readAllBytes()).strip();
        assertEquals(0, proc.waitFor(), "postprocess.py exited with non-zero code");

        JsonObject helperAnalysis = GSON.fromJson(stdout, JsonObject.class);
        assertAnalysisClose(helperAnalysis, data.getAsJsonObject("analysis"));

        HttpRequest req = HttpRequest.newBuilder().uri(URI.create(BASE_URL + "/latest-report")).build();
        HttpResponse<String> resp = CLIENT.send(req, HttpResponse.BodyHandlers.ofString());
        assertEquals(200, resp.statusCode());
        assertAnalysisClose(GSON.fromJson(resp.body(), JsonObject.class), helperAnalysis);
    }

    @Test
    @Order(4)
    void test_analysis_fields_are_consistent_with_profiles() throws Exception {
        /** Verify that analysis fields (mean, population stddev, pressure drop, regime) are
            mathematically consistent with the returned simulation profiles. */
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("viscosity", 0.08);
        payload.put("inlet_velocity", 2.8);
        payload.put("grid_points", 8);
        payload.put("steps", 6);
        JsonObject data = runSimulation(payload);

        JsonArray velArr  = data.getAsJsonArray("velocity_profile");
        JsonArray presArr = data.getAsJsonArray("pressure_profile");

        double[] vel  = new double[velArr.size()];
        double[] pres = new double[presArr.size()];
        for (int i = 0; i < velArr.size();  i++) vel[i]  = velArr.get(i).getAsDouble();
        for (int i = 0; i < presArr.size(); i++) pres[i] = presArr.get(i).getAsDouble();

        double mean     = Arrays.stream(vel).average().getAsDouble();
        double variance = Arrays.stream(vel).map(v -> (v - mean) * (v - mean)).average().getAsDouble();
        double pstdev   = Math.sqrt(variance);
        double pressDrop = pres[0] - pres[pres.length - 1];

        JsonObject analysis = data.getAsJsonObject("analysis");
        assertClose(analysis.get("mean_velocity").getAsDouble(),   mean);
        assertClose(analysis.get("velocity_stddev").getAsDouble(), pstdev);
        assertClose(analysis.get("pressure_drop").getAsDouble(),   pressDrop);
        assertTrue(Set.of("laminar", "transitional", "turbulent")
            .contains(analysis.get("dominant_regime").getAsString()));
    }

    @Test
    @Order(5)
    void test_inputs_change_the_simulation() throws Exception {
        /** Verify that changing viscosity and inlet_velocity genuinely modifies physics output,
            checking inverse relationships and that dominant_regime varies with Reynolds number. */
        // Viscosity sensitivity
        Map<String, Object> lowViscPayload = new LinkedHashMap<>();
        lowViscPayload.put("viscosity", 0.05); lowViscPayload.put("inlet_velocity", 3.0);
        lowViscPayload.put("grid_points", 6);  lowViscPayload.put("steps", 4);
        JsonObject lowVisc = runSimulation(lowViscPayload);

        Map<String, Object> highViscPayload = new LinkedHashMap<>();
        highViscPayload.put("viscosity", 0.25); highViscPayload.put("inlet_velocity", 3.0);
        highViscPayload.put("grid_points", 6);  highViscPayload.put("steps", 4);
        JsonObject highVisc = runSimulation(highViscPayload);

        assertTrue(lowVisc.get("reynolds_number").getAsDouble() > highVisc.get("reynolds_number").getAsDouble());
        assertTrue(
            lowVisc.getAsJsonObject("analysis").get("mean_velocity").getAsDouble() >
            highVisc.getAsJsonObject("analysis").get("mean_velocity").getAsDouble()
        );
        assertFalse(Math.abs(
            lowVisc.getAsJsonObject("analysis").get("pressure_drop").getAsDouble() -
            highVisc.getAsJsonObject("analysis").get("pressure_drop").getAsDouble()
        ) <= 1e-6);

        // Inlet velocity sensitivity
        Map<String, Object> slowPayload = new LinkedHashMap<>();
        slowPayload.put("viscosity", 0.1); slowPayload.put("inlet_velocity", 1.0);
        slowPayload.put("grid_points", 6); slowPayload.put("steps", 4);
        JsonObject slowVel = runSimulation(slowPayload);

        Map<String, Object> fastPayload = new LinkedHashMap<>();
        fastPayload.put("viscosity", 0.1); fastPayload.put("inlet_velocity", 5.0);
        fastPayload.put("grid_points", 6); fastPayload.put("steps", 4);
        JsonObject fastVel = runSimulation(fastPayload);

        assertTrue(fastVel.get("reynolds_number").getAsDouble() > slowVel.get("reynolds_number").getAsDouble());
        assertTrue(
            fastVel.getAsJsonObject("analysis").get("mean_velocity").getAsDouble() >
            slowVel.getAsJsonObject("analysis").get("mean_velocity").getAsDouble()
        );

        // Regime change check
        Map<String, Object> veryLowRePayload = new LinkedHashMap<>();
        veryLowRePayload.put("viscosity", 5.0); veryLowRePayload.put("inlet_velocity", 1.0);
        veryLowRePayload.put("grid_points", 6); veryLowRePayload.put("steps", 4);
        JsonObject veryLowRe = runSimulation(veryLowRePayload);

        Map<String, Object> veryHighRePayload = new LinkedHashMap<>();
        veryHighRePayload.put("viscosity", 0.001); veryHighRePayload.put("inlet_velocity", 5.0);
        veryHighRePayload.put("grid_points", 6);   veryHighRePayload.put("steps", 4);
        JsonObject veryHighRe = runSimulation(veryHighRePayload);

        assertNotEquals(
            veryLowRe.getAsJsonObject("analysis").get("dominant_regime").getAsString(),
            veryHighRe.getAsJsonObject("analysis").get("dominant_regime").getAsString(),
            "dominant_regime must vary with Reynolds number"
        );
    }
}
