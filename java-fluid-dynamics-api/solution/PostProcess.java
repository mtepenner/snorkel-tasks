import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class PostProcess {
    public static void main(String[] args) throws IOException {
        if (args.length < 1) {
            throw new IllegalArgumentException("usage: PostProcess <simulation-json> [output-json]");
        }

        Path simulationPath = Path.of(args[0]);
        String simulationJson = Files.readString(simulationPath);

        double[] velocityProfile = extractDoubleArray(simulationJson, "velocity_profile");
        double[] pressureProfile = extractDoubleArray(simulationJson, "pressure_profile");
        double reynoldsNumber = extractDouble(simulationJson, "reynolds_number");

        String analysisJson = buildAnalysisJson(velocityProfile, pressureProfile, reynoldsNumber);
        if (args.length > 1) {
            Files.writeString(Path.of(args[1]), analysisJson);
        }

        System.out.println(analysisJson);
    }

    private static String buildAnalysisJson(double[] velocityProfile, double[] pressureProfile, double reynoldsNumber) {
        double meanVelocity = mean(velocityProfile);
        double variance = 0.0;
        for (double value : velocityProfile) {
            double delta = value - meanVelocity;
            variance += delta * delta;
        }
        variance /= velocityProfile.length;
        double pressureDrop = pressureProfile[0] - pressureProfile[pressureProfile.length - 1];

        return "{" +
                "\"mean_velocity\":" + formatDouble(meanVelocity) + "," +
                "\"velocity_stddev\":" + formatDouble(Math.sqrt(variance)) + "," +
                "\"pressure_drop\":" + formatDouble(pressureDrop) + "," +
                "\"dominant_regime\":\"" + dominantRegime(reynoldsNumber) + "\"" +
                "}";
    }

    private static double mean(double[] values) {
        double sum = 0.0;
        for (double value : values) {
            sum += value;
        }
        return sum / values.length;
    }

    private static String dominantRegime(double reynoldsNumber) {
        if (reynoldsNumber < 50) {
            return "laminar";
        }
        if (reynoldsNumber < 150) {
            return "transitional";
        }
        return "turbulent";
    }

    private static String formatDouble(double value) {
        return String.format(Locale.US, "%.6f", value);
    }

    private static double extractDouble(String json, String key) {
        Matcher matcher = Pattern.compile("\\\"" + Pattern.quote(key) + "\\\"\\s*:\\s*(-?\\d+(?:\\.\\d+)?)").matcher(json);
        if (!matcher.find()) {
            throw new IllegalArgumentException("missing field: " + key);
        }
        return Double.parseDouble(matcher.group(1));
    }

    private static double[] extractDoubleArray(String json, String key) {
        Matcher matcher = Pattern.compile("\\\"" + Pattern.quote(key) + "\\\"\\s*:\\s*\\[(.*?)]").matcher(json);
        if (!matcher.find()) {
            throw new IllegalArgumentException("missing array field: " + key);
        }

        String raw = matcher.group(1).trim();
        if (raw.isEmpty()) {
            return new double[0];
        }

        String[] parts = raw.split(",");
        double[] values = new double[parts.length];
        for (int index = 0; index < parts.length; index++) {
            values[index] = Double.parseDouble(parts[index].trim());
        }
        return values;
    }
}