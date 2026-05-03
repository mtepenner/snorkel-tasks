import com.google.gson.Gson;
import com.google.gson.JsonObject;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDDocumentInformation;
import org.apache.pdfbox.pdmodel.PDPage;
import org.apache.pdfbox.pdmodel.PDPageContentStream;
import org.apache.pdfbox.pdmodel.common.PDRectangle;
import org.apache.pdfbox.pdmodel.font.PDType1Font;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Order;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.MethodOrderer.OrderAnnotation;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

@TestMethodOrder(OrderAnnotation.class)
public class TestOutputs {

    private static final Path API_PATH = Path.of("/app/workspace/src/LongMetadataApi.java");
    private static final Path UI_PATH = Path.of("/app/workspace/src/static/index.html");
    private static final String BASE_URL = "http://127.0.0.1:8000";
    private static final Set<String> EXPECTED_KEYS = Set.of(
        "author", "title", "topics", "total_chunks", "filename", "total_words"
    );
    private static final Set<String> STOP_WORDS = Set.of(
        "the", "to", "a", "an", "is", "in", "and", "of", "for", "it",
        "this", "that", "was", "are", "were", "with", "from", "but",
        "or", "not", "have", "has", "had", "been", "being",
        "will", "would", "could", "should", "about", "which",
        "there", "their", "they", "then", "than", "them"
    );
    private static final Set<String> PDF_TOPIC_WORDS = Set.of(
        "dummy", "long", "context", "line", "test", "chunking", "mechanisms"
    );
    private static final HttpClient CLIENT = HttpClient.newHttpClient();
    private static final Gson GSON = new Gson();
    private static Process serverProcess;

    @BeforeAll
    static void setupAll() throws Exception {
        assertTrue(Files.exists(API_PATH), "LongMetadataApi.java is missing");
        assertTrue(Files.exists(UI_PATH), "static/index.html is missing");

        Files.createDirectories(Path.of("/tmp/app-classes"));
        Process compile = new ProcessBuilder(
            "javac",
            "-cp",
            "/usr/share/java/*",
            API_PATH.toString(),
            "-d",
            "/tmp/app-classes"
        ).inheritIO().start();
        assertEquals(0, compile.waitFor(), "javac compilation failed");

        serverProcess = new ProcessBuilder(
            "java",
            "-cp",
            "/tmp/app-classes:/usr/share/java/*",
            "LongMetadataApi"
        ).directory(new File("/app/workspace/src")).start();

        waitForServer();
    }

    @AfterAll
    static void teardownAll() {
        if (serverProcess != null) {
            serverProcess.destroy();
        }
    }

    @Test
    @Order(1)
    void test_required_files_exist() {
        assertTrue(Files.exists(API_PATH), "Java API file missing.");
        assertTrue(Files.exists(UI_PATH), "GUI file missing.");
    }

    @Test
    @Order(2)
    void test_static_ui_accessible_and_functional() throws Exception {
        HttpResponse<String> response = CLIENT.send(
            HttpRequest.newBuilder(URI.create(BASE_URL + "/static/index.html")).build(),
            HttpResponse.BodyHandlers.ofString()
        );
        assertEquals(200, response.statusCode(), "GUI endpoint non-200.");

        String html = response.body().toLowerCase();
        assertTrue(html.contains("type=\"file\""), "UI missing file upload.");
        assertTrue(html.contains("fetch("), "UI missing API call logic.");
        assertTrue(
            html.contains("json.stringify") || html.contains("textcontent") || html.contains("innerhtml") || html.contains("innertext"),
            "UI does not render the API response."
        );
    }

    @Test
    @Order(3)
    void test_extract_rejects_get_requests() throws Exception {
        HttpResponse<String> response = CLIENT.send(
            HttpRequest.newBuilder(URI.create(BASE_URL + "/extract")).build(),
            HttpResponse.BodyHandlers.ofString()
        );
        assertEquals(405, response.statusCode(), "GET /extract should not be allowed.");
    }

    @Test
    @Order(4)
    void test_extraction_fallback_and_chunking() throws Exception {
        Path pdfPath = Path.of("/tmp/fallback_test.pdf");
        createDummyPdf(pdfPath, false);

        JsonObject data = postExtract(pdfPath, "fallback_test.pdf");

        assertEquals(EXPECTED_KEYS, new HashSet<>(data.keySet()), "Unexpected response keys.");
        assertEquals("Unknown Author", data.get("author").getAsString());
        assertEquals("Untitled", data.get("title").getAsString());
        assertEquals("fallback_test.pdf", data.get("filename").getAsString());

        int totalWords = data.get("total_words").getAsInt();
        int totalChunks = data.get("total_chunks").getAsInt();

        assertTrue(totalWords >= 2000 && totalWords <= 10000, "Unexpected total_words range.");
        assertTrue(totalChunks >= 3, "Expected >=3 chunks for large dummy PDF.");
        assertEquals((int) Math.ceil(totalWords / 1000.0), totalChunks, "Chunk count math is wrong.");

        List<String> topics = jsonArrayToLowerList(data, "topics");
        assertTrue(topics.size() >= 3 && topics.size() <= 10, "topics must contain between 3 and 10 keywords.");
        assertTrue(topics.stream().allMatch(topic -> !topic.isBlank()), "topics must be non-empty.");
        assertTrue(topics.stream().allMatch(topic -> !topic.contains(" ")), "topics must be single-word tokens.");
        assertTrue(topics.stream().allMatch(topic -> topic.length() >= 4), "Each topic must be at least 4 chars.");

        Set<String> foundTopics = new HashSet<>(topics);
        foundTopics.retainAll(STOP_WORDS);
        assertTrue(foundTopics.isEmpty(), "Topics contain obvious stop words.");

        Set<String> matched = new HashSet<>(topics);
        matched.retainAll(PDF_TOPIC_WORDS);
        assertTrue(matched.size() >= 3, "Expected >=3 topic keywords from the PDF text.");
    }

    @Test
    @Order(5)
    void test_chunk_boundary_uses_1000_word_cap() throws Exception {
        Path pdfPath = Path.of("/tmp/boundary_test.pdf");
        createBoundaryPdf(pdfPath, 1001);

        JsonObject data = postExtract(pdfPath, "boundary_test.pdf");
        int totalWords = data.get("total_words").getAsInt();
        int totalChunks = data.get("total_chunks").getAsInt();

        assertTrue(totalWords >= 1001 && totalWords < 2000, "Boundary test expected between 1001 and 1999 words.");
        assertEquals(2, totalChunks, "Expected exactly 2 chunks for the boundary PDF.");
    }

    @Test
    @Order(6)
    void test_extraction_positive_metadata() throws Exception {
        Path pdfPath = Path.of("/tmp/meta_test.pdf");
        createDummyPdf(pdfPath, true);

        JsonObject data = postExtract(pdfPath, "meta_test.pdf");
        assertEquals("Jane Doe", data.get("author").getAsString(), "Failed to extract correct author.");
        assertEquals("My Report", data.get("title").getAsString(), "Failed to extract correct title.");
    }

    @Test
    @Order(7)
    void test_topics_sorted_by_frequency() throws Exception {
        Path pdfPath = Path.of("/tmp/frequency_test.pdf");
        createFrequencyPdf(pdfPath);

        JsonObject data = postExtract(pdfPath, "frequency_test.pdf");
        List<String> topics = jsonArrayToLowerList(data, "topics");

        assertTrue(topics.contains("elephant"), "High-frequency word 'elephant' must appear in topics.");
        assertTrue(topics.contains("tiger"), "Mid-frequency word 'tiger' must appear in topics.");
        assertTrue(
            topics.indexOf("elephant") < topics.indexOf("tiger"),
            "Topics must be sorted by descending frequency."
        );
    }

    private static void waitForServer() throws Exception {
        HttpRequest request = HttpRequest.newBuilder(URI.create(BASE_URL + "/static/index.html")).build();
        for (int attempt = 0; attempt < 30; attempt++) {
            try {
                HttpResponse<String> response = CLIENT.send(request, HttpResponse.BodyHandlers.ofString());
                if (response.statusCode() == 200) {
                    return;
                }
            } catch (Exception ignored) {
            }
            Thread.sleep(500);
        }
        throw new AssertionError("Java API did not become ready on port 8000");
    }

    private static JsonObject postExtract(Path pdfPath, String filename) throws Exception {
        String boundary = "Boundary" + UUID.randomUUID().toString().replace("-", "");
        ByteArrayOutputStream body = new ByteArrayOutputStream();
        body.write(("--" + boundary + "\r\n").getBytes(StandardCharsets.UTF_8));
        body.write((
            "Content-Disposition: form-data; name=\"file\"; filename=\"" + filename + "\"\r\n" +
            "Content-Type: application/pdf\r\n\r\n"
        ).getBytes(StandardCharsets.UTF_8));
        body.write(Files.readAllBytes(pdfPath));
        body.write(("\r\n--" + boundary + "--\r\n").getBytes(StandardCharsets.UTF_8));

        HttpRequest request = HttpRequest.newBuilder(URI.create(BASE_URL + "/extract"))
            .header("Content-Type", "multipart/form-data; boundary=" + boundary)
            .POST(HttpRequest.BodyPublishers.ofByteArray(body.toByteArray()))
            .build();

        HttpResponse<String> response = CLIENT.send(request, HttpResponse.BodyHandlers.ofString());
        assertEquals(200, response.statusCode(), "POST /extract failed: " + response.body());
        return GSON.fromJson(response.body(), JsonObject.class);
    }

    private static List<String> jsonArrayToLowerList(JsonObject object, String key) {
        List<String> values = new ArrayList<>();
        object.getAsJsonArray(key).forEach(element -> values.add(element.getAsString().toLowerCase()));
        return values;
    }

    private static void createDummyPdf(Path path, boolean withMetadata) throws Exception {
        List<String> lines = new ArrayList<>();
        for (int i = 1; i < 300; i++) {
            lines.add(
                "Dummy long context line " + i +
                " to test chunking mechanisms dummy long context line " + i +
                " to test chunking mechanisms"
            );
        }
        writePdf(path, lines, withMetadata ? "Jane Doe" : null, withMetadata ? "My Report" : null);
    }

    private static void createBoundaryPdf(Path path, int wordCount) throws Exception {
        List<String> words = new ArrayList<>();
        for (int index = 0; index < wordCount; index++) {
            words.add("alpha");
        }

        List<String> lines = new ArrayList<>();
        for (int start = 0; start < words.size(); start += 20) {
            lines.add(String.join(" ", words.subList(start, Math.min(start + 20, words.size()))));
        }
        writePdf(path, lines, null, null);
    }

    private static void createFrequencyPdf(Path path) throws Exception {
        List<String> words = new ArrayList<>();
        words.addAll(repeat("elephant", 150));
        words.addAll(repeat("tiger", 60));
        words.addAll(repeat("python", 20));

        List<String> lines = new ArrayList<>();
        for (int start = 0; start < words.size(); start += 15) {
            lines.add(String.join(" ", words.subList(start, Math.min(start + 15, words.size()))));
        }
        writePdf(path, lines, null, null);
    }

    private static List<String> repeat(String token, int count) {
        String[] values = new String[count];
        Arrays.fill(values, token);
        return Arrays.asList(values);
    }

    private static void writePdf(Path path, List<String> lines, String author, String title) throws Exception {
        try (PDDocument document = new PDDocument()) {
            if (author != null || title != null) {
                PDDocumentInformation info = new PDDocumentInformation();
                if (author != null) {
                    info.setAuthor(author);
                }
                if (title != null) {
                    info.setTitle(title);
                }
                document.setDocumentInformation(info);
            }

            PDPage page = null;
            PDPageContentStream stream = null;
            float margin = 50;
            float fontSize = 12;
            float leading = 14;
            float cursorY = 0;

            for (String line : lines) {
                if (stream == null || cursorY < margin) {
                    if (stream != null) {
                        stream.endText();
                        stream.close();
                    }
                    page = new PDPage(PDRectangle.LETTER);
                    document.addPage(page);
                    stream = new PDPageContentStream(document, page);
                    stream.beginText();
                    stream.setFont(PDType1Font.HELVETICA, fontSize);
                    cursorY = page.getMediaBox().getHeight() - margin;
                    stream.newLineAtOffset(margin, cursorY);
                }

                stream.showText(line);
                stream.newLineAtOffset(0, -leading);
                cursorY -= leading;
            }

            if (stream != null) {
                stream.endText();
                stream.close();
            }

            document.save(path.toFile());
        }
    }
}