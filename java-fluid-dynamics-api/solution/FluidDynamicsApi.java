import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.Locale;
import java.util.concurrent.Executors;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class FluidDynamicsApi {
    private static final Path DATA_DIR = Paths.get("/app/workspace/data");
    private static final Path SIMULATION_FILE = DATA_DIR.resolve("latest_simulation.json");
    private static final Path ANALYSIS_FILE = DATA_DIR.resolve("latest_analysis.json");

    public static void main(String[] args) throws Exception {
        Files.createDirectories(DATA_DIR);

        HttpServer server = HttpServer.create(new InetSocketAddress("0.0.0.0", 8080), 0);
        server.createContext("/health", exchange -> writeJson(exchange, 200, "{\"status\":\"ok\"}"));
        server.createContext("/latest-report", new LatestReportHandler());
        server.createContext("/simulate", new SimulationHandler());
        server.setExecutor(Executors.newCachedThreadPool());
        server.start();
    }

    private static class LatestReportHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!"GET".equalsIgnoreCase(exchange.getRequestMethod())) {
                writeJson(exchange, 405, "{\"error\":\"Method not allowed\"}");
                return;
            }

            if (!Files.exists(ANALYSIS_FILE)) {
                writeJson(exchange, 404, "{\"error\":\"No analysis available\"}");
                return;
            }

            writeJson(exchange, 200, Files.readString(ANALYSIS_FILE));
        }
    }

    private static class SimulationHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!"POST".equalsIgnoreCase(exchange.getRequestMethod())) {
                writeJson(exchange, 405, "{\"error\":\"Method not allowed\"}");
                return;
            }

            try {
                String requestBody = readBody(exchange.getRequestBody());
                double viscosity = extractDouble(requestBody, "viscosity");
                double inletVelocity = extractDouble(requestBody, "inlet_velocity");
                int gridPoints = extractInt(requestBody, "grid_points");
                int steps = extractInt(requestBody, "steps");

                if (viscosity <= 0 || inletVelocity <= 0 || gridPoints < 3 || steps < 1) {
                    throw new IllegalArgumentException("invalid simulation parameters");
                }

                SimulationResult result = simulate(viscosity, inletVelocity, gridPoints, steps);
                Files.writeString(SIMULATION_FILE, result.toSimulationJson());

                Process process = new ProcessBuilder(
                    pythonCommand(),
                        "/app/workspace/src/postprocess.py",
                        SIMULATION_FILE.toString(),
                        ANALYSIS_FILE.toString()
                ).redirectErrorStream(true).start();

                String analysisJson = new String(process.getInputStream().readAllBytes(), StandardCharsets.UTF_8).trim();
                try {
                    int exitCode = process.waitFor();
                    if (exitCode != 0 || analysisJson.isEmpty()) {
                        throw new IllegalStateException("python post-process failed");
                    }
                } catch (InterruptedException interruptedException) {
                    Thread.currentThread().interrupt();
                    throw new IllegalStateException("python post-process interrupted");
                }

                writeJson(exchange, 200, result.toResponseJson(analysisJson));
            } catch (IllegalArgumentException illegalArgumentException) {
                writeJson(exchange, 400, "{\"error\":\"" + escapeJson(illegalArgumentException.getMessage()) + "\"}");
            } catch (Exception exception) {
                writeJson(exchange, 500, "{\"error\":\"internal error\"}");
            }
        }
    }

    private static SimulationResult simulate(double viscosity, double inletVelocity, int gridPoints, int steps) {
        double[] velocity = new double[gridPoints];
        double[] pressure = new double[gridPoints];
        double dx = 1.0 / (gridPoints - 1);

        for (int index = 0; index < gridPoints; index++) {
            double position = index * dx;
            velocity[index] = Math.max(0.0, inletVelocity * (1.0 - 0.12 * position));
        }

        for (int step = 0; step < steps; step++) {
            double[] nextVelocity = Arrays.copyOf(velocity, velocity.length);
            nextVelocity[0] = inletVelocity;

            for (int index = 1; index < gridPoints; index++) {
                double upstream = velocity[index - 1];
                double current = velocity[index];
                double diffusion = viscosity * (upstream - current) * 0.65;
                double damping = current * viscosity * dx * (0.4 + step * 0.05);
                nextVelocity[index] = Math.max(0.0, current + diffusion - damping);
            }

            velocity = nextVelocity;
        }

        double basePressure = inletVelocity * inletVelocity * 0.5 + viscosity * steps * 8.0;
        pressure[0] = basePressure;
        for (int index = 1; index < gridPoints; index++) {
            double drop = viscosity * inletVelocity * (1.5 + index * dx) + steps * 0.08;
            pressure[index] = Math.max(0.0, pressure[index - 1] - drop);
        }

        double reynoldsNumber = (inletVelocity * gridPoints) / viscosity;
        return new SimulationResult(viscosity, inletVelocity, gridPoints, steps, reynoldsNumber, velocity, pressure);
    }

    private static String readBody(InputStream inputStream) throws IOException {
        return new String(inputStream.readAllBytes(), StandardCharsets.UTF_8);
    }

    private static double extractDouble(String json, String key) {
        Matcher matcher = Pattern.compile("\\\"" + Pattern.quote(key) + "\\\"\\s*:\\s*(-?\\d+(?:\\.\\d+)?)").matcher(json);
        if (!matcher.find()) {
            throw new IllegalArgumentException("missing field: " + key);
        }
        return Double.parseDouble(matcher.group(1));
    }

    private static int extractInt(String json, String key) {
        return (int) Math.round(extractDouble(json, key));
    }

    private static void writeJson(HttpExchange exchange, int statusCode, String payload) throws IOException {
        byte[] encoded = payload.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json");
        exchange.sendResponseHeaders(statusCode, encoded.length);
        try (OutputStream outputStream = exchange.getResponseBody()) {
            outputStream.write(encoded);
        }
    }

    private static String escapeJson(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private static String formatDouble(double value) {
        return String.format(Locale.US, "%.6f", value);
    }

    private static String pythonCommand() {
        String osName = System.getProperty("os.name", "").toLowerCase(Locale.ROOT);
        if (osName.contains("win")) {
            return "python";
        }
        return "python3";
    }

    private record SimulationResult(
            double viscosity,
            double inletVelocity,
            int gridPoints,
            int steps,
            double reynoldsNumber,
            double[] velocityProfile,
            double[] pressureProfile
    ) {
        private String toSimulationJson() {
            return "{" +
                    "\"viscosity\":" + formatDouble(viscosity) + "," +
                    "\"inlet_velocity\":" + formatDouble(inletVelocity) + "," +
                    "\"grid_points\":" + gridPoints + "," +
                    "\"steps\":" + steps + "," +
                    "\"reynolds_number\":" + formatDouble(reynoldsNumber) + "," +
                    "\"velocity_profile\":" + arrayToJson(velocityProfile) + "," +
                    "\"pressure_profile\":" + arrayToJson(pressureProfile) +
                    "}";
        }

        private String toResponseJson(String analysisJson) {
            return "{" +
                    "\"viscosity\":" + formatDouble(viscosity) + "," +
                    "\"inlet_velocity\":" + formatDouble(inletVelocity) + "," +
                    "\"grid_points\":" + gridPoints + "," +
                    "\"steps\":" + steps + "," +
                    "\"reynolds_number\":" + formatDouble(reynoldsNumber) + "," +
                    "\"velocity_profile\":" + arrayToJson(velocityProfile) + "," +
                    "\"pressure_profile\":" + arrayToJson(pressureProfile) + "," +
                    "\"analysis\":" + analysisJson +
                    "}";
        }

        private static String arrayToJson(double[] values) {
            StringBuilder builder = new StringBuilder("[");
            for (int index = 0; index < values.length; index++) {
                if (index > 0) {
                    builder.append(',');
                }
                builder.append(formatDouble(values[index]));
            }
            return builder.append(']').toString();
        }
    }
}