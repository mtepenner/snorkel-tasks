import com.sun.net.httpserver.Headers;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.pdmodel.PDDocumentInformation;
import org.apache.pdfbox.text.PDFTextStripper;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Executors;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class LongMetadataApi {
    private static final Path STATIC_DIR = Paths.get("/app/workspace/src/static");
    private static final Pattern BOUNDARY_PATTERN = Pattern.compile("boundary=(?:\"([^\"]+)\"|([^;]+))");
    private static final Pattern FILENAME_PATTERN = Pattern.compile("filename=\"([^\"]*)\"");
    private static final byte[] CRLF = "\r\n".getBytes(StandardCharsets.ISO_8859_1);
    private static final byte[] HEADER_SPLIT = "\r\n\r\n".getBytes(StandardCharsets.ISO_8859_1);
    private static final Set<String> STOP_WORDS = Set.of(
        "the", "to", "a", "an", "is", "in", "and", "of", "for", "it",
        "this", "that", "was", "are", "were", "with", "from", "but",
        "or", "not", "have", "has", "had", "been", "being",
        "will", "would", "could", "should", "about", "which",
        "there", "their", "they", "then", "than", "them"
    );

    public static void main(String[] args) throws Exception {
        Files.createDirectories(STATIC_DIR);

        HttpServer server = HttpServer.create(new InetSocketAddress("0.0.0.0", 8000), 0);
        server.createContext("/extract", new ExtractHandler());
        server.createContext("/static", new StaticHandler());
        server.setExecutor(Executors.newCachedThreadPool());
        server.start();
    }

    private static final class ExtractHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!"POST".equalsIgnoreCase(exchange.getRequestMethod())) {
                writeJson(exchange, 405, "{\"error\":\"Method not allowed\"}");
                return;
            }

            try {
                UploadedFile uploadedFile = parseMultipart(
                    exchange.getRequestBody().readAllBytes(),
                    exchange.getRequestHeaders().getFirst("Content-Type")
                );
                ExtractionResult result = extract(uploadedFile);
                writeJson(exchange, 200, result.toJson());
            } catch (IllegalArgumentException illegalArgumentException) {
                writeJson(exchange, 400, errorJson(illegalArgumentException.getMessage()));
            }
        }
    }

    private static final class StaticHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String requestPath = exchange.getRequestURI().getPath();
            String relative = requestPath.equals("/static") || requestPath.equals("/static/")
                ? "index.html"
                : requestPath.substring("/static/".length());

            relative = URLDecoder.decode(relative, StandardCharsets.UTF_8);
            Path target = STATIC_DIR.resolve(relative).normalize();
            if (!target.startsWith(STATIC_DIR) || !Files.exists(target) || Files.isDirectory(target)) {
                writeJson(exchange, 404, "{\"error\":\"Not found\"}");
                return;
            }

            byte[] body = Files.readAllBytes(target);
            Headers headers = exchange.getResponseHeaders();
            headers.set("Content-Type", contentTypeFor(target));
            exchange.sendResponseHeaders(200, body.length);
            try (OutputStream outputStream = exchange.getResponseBody()) {
                outputStream.write(body);
            }
        }
    }

    private static ExtractionResult extract(UploadedFile uploadedFile) throws IOException {
        try (PDDocument document = PDDocument.load(uploadedFile.contents())) {
            PDDocumentInformation info = document.getDocumentInformation();
            String author = fallback(info == null ? null : info.getAuthor(), "Unknown Author");
            String title = fallback(info == null ? null : info.getTitle(), "Untitled");
            String text = new PDFTextStripper().getText(document);
            List<String> words = splitWords(text);

            int totalWords = words.size();
            int totalChunks = totalWords == 0 ? 0 : (int) Math.ceil(totalWords / 1000.0);
            List<String> topics = extractTopics(text);

            return new ExtractionResult(author, title, topics, totalChunks, uploadedFile.filename(), totalWords);
        }
    }

    private static UploadedFile parseMultipart(byte[] body, String contentType) {
        if (contentType == null || !contentType.toLowerCase(Locale.ROOT).startsWith("multipart/form-data")) {
            throw new IllegalArgumentException("expected multipart/form-data");
        }

        Matcher boundaryMatcher = BOUNDARY_PATTERN.matcher(contentType);
        if (!boundaryMatcher.find()) {
            throw new IllegalArgumentException("missing multipart boundary");
        }

        String boundaryValue = boundaryMatcher.group(1) != null ? boundaryMatcher.group(1) : boundaryMatcher.group(2);
        String boundary = "--" + boundaryValue;
        byte[] boundaryBytes = boundary.getBytes(StandardCharsets.ISO_8859_1);
        byte[] nextBoundary = ("\r\n" + boundary).getBytes(StandardCharsets.ISO_8859_1);

        int firstBoundary = indexOf(body, boundaryBytes, 0);
        if (firstBoundary != 0) {
            throw new IllegalArgumentException("invalid multipart body");
        }

        int headersStart = firstBoundary + boundaryBytes.length + CRLF.length;
        int headersEnd = indexOf(body, HEADER_SPLIT, headersStart);
        if (headersEnd < 0) {
            throw new IllegalArgumentException("missing multipart headers");
        }

        String headers = new String(body, headersStart, headersEnd - headersStart, StandardCharsets.ISO_8859_1);
        if (!headers.toLowerCase(Locale.ROOT).contains("name=\"file\"")) {
            throw new IllegalArgumentException("upload field must be named file");
        }

        Matcher filenameMatcher = FILENAME_PATTERN.matcher(headers);
        if (!filenameMatcher.find()) {
            throw new IllegalArgumentException("missing uploaded filename");
        }

        int fileStart = headersEnd + HEADER_SPLIT.length;
        int fileEnd = indexOf(body, nextBoundary, fileStart);
        if (fileEnd < 0) {
            throw new IllegalArgumentException("multipart body missing closing boundary");
        }

        byte[] fileBytes = new byte[fileEnd - fileStart];
        System.arraycopy(body, fileStart, fileBytes, 0, fileBytes.length);
        return new UploadedFile(filenameMatcher.group(1), fileBytes);
    }

    private static List<String> splitWords(String text) {
        String trimmed = text == null ? "" : text.trim();
        if (trimmed.isEmpty()) {
            return List.of();
        }

        String[] pieces = trimmed.split("\\s+");
        List<String> words = new ArrayList<>(pieces.length);
        for (String piece : pieces) {
            if (!piece.isEmpty()) {
                words.add(piece);
            }
        }
        return words;
    }

    private static List<String> extractTopics(String text) {
        Matcher matcher = Pattern.compile("[A-Za-z]{4,}").matcher(text == null ? "" : text.toLowerCase(Locale.ROOT));
        Map<String, Integer> frequencies = new HashMap<>();
        while (matcher.find()) {
            String token = matcher.group();
            if (!STOP_WORDS.contains(token)) {
                frequencies.merge(token, 1, Integer::sum);
            }
        }

        return frequencies.entrySet().stream()
            .sorted(Comparator.<Map.Entry<String, Integer>>comparingInt(Map.Entry::getValue).reversed()
                .thenComparing(Map.Entry::getKey))
            .limit(10)
            .map(Map.Entry::getKey)
            .toList();
    }

    private static String fallback(String value, String fallback) {
        return value == null || value.isBlank() ? fallback : value;
    }

    private static int indexOf(byte[] haystack, byte[] needle, int startIndex) {
        outer:
        for (int index = Math.max(0, startIndex); index <= haystack.length - needle.length; index++) {
            for (int offset = 0; offset < needle.length; offset++) {
                if (haystack[index + offset] != needle[offset]) {
                    continue outer;
                }
            }
            return index;
        }
        return -1;
    }

    private static void writeJson(HttpExchange exchange, int statusCode, String payload) throws IOException {
        byte[] encoded = payload.getBytes(StandardCharsets.UTF_8);
        exchange.getResponseHeaders().set("Content-Type", "application/json");
        exchange.sendResponseHeaders(statusCode, encoded.length);
        try (OutputStream outputStream = exchange.getResponseBody()) {
            outputStream.write(encoded);
        }
    }

    private static String contentTypeFor(Path path) {
        String name = path.getFileName().toString().toLowerCase(Locale.ROOT);
        if (name.endsWith(".html")) {
            return "text/html; charset=utf-8";
        }
        if (name.endsWith(".js")) {
            return "application/javascript; charset=utf-8";
        }
        if (name.endsWith(".css")) {
            return "text/css; charset=utf-8";
        }
        return "application/octet-stream";
    }

    private static String errorJson(String message) {
        return "{\"error\":\"" + escapeJson(message) + "\"}";
    }

    private static String escapeJson(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"");
    }

    private record UploadedFile(String filename, byte[] contents) {
    }

    private record ExtractionResult(
        String author,
        String title,
        List<String> topics,
        int totalChunks,
        String filename,
        int totalWords
    ) {
        private String toJson() {
            Map<String, String> fields = new LinkedHashMap<>();
            fields.put("author", quote(author));
            fields.put("title", quote(title));
            fields.put("topics", topicsJson());
            fields.put("total_chunks", Integer.toString(totalChunks));
            fields.put("filename", quote(filename));
            fields.put("total_words", Integer.toString(totalWords));

            StringBuilder builder = new StringBuilder("{");
            boolean first = true;
            for (Map.Entry<String, String> entry : fields.entrySet()) {
                if (!first) {
                    builder.append(',');
                }
                first = false;
                builder.append('"').append(entry.getKey()).append('"').append(':').append(entry.getValue());
            }
            return builder.append('}').toString();
        }

        private String topicsJson() {
            StringBuilder builder = new StringBuilder("[");
            for (int index = 0; index < topics.size(); index++) {
                if (index > 0) {
                    builder.append(',');
                }
                builder.append(quote(topics.get(index)));
            }
            return builder.append(']').toString();
        }

        private String quote(String value) {
            return '"' + escapeJson(value) + '"';
        }
    }
}