using Models;

namespace Services
{
    public static class GptParser
    {
        public static List<RoleBlock> ParseRoles(string gptText)
        {
            var lines = gptText.Split('\n');
            var roles = new List<RoleBlock>();
            RoleBlock? current = null;

            foreach (var line in lines.Select(l => l.Trim()))
            {
                if (line.StartsWith("### ROLE"))
                {
                    if (current != null) roles.Add(current);
                    current = new RoleBlock();
                }
                else if (current != null && string.IsNullOrEmpty(current.Title) && !string.IsNullOrEmpty(line) && !line.StartsWith("-"))
                {
                    // Try to parse "Title | Company | Date" format first
                    var parts = line.Split('|');
                    if (parts.Length >= 3)
                    {
                        current.Title = parts[0].Trim() + " | " + parts[1].Trim();
                        current.Date = parts[2].Trim();
                    }
                    else
                    {
                        // New format: Title and Date are on separate lines
                        current.Title = line;
                    }
                }
                else if (current != null && !string.IsNullOrEmpty(current.Title) && string.IsNullOrEmpty(current.Date) && !string.IsNullOrEmpty(line) && !line.StartsWith("-"))
                {
                    // This is the date line (next line after title)
                    current.Date = line;
                }
                else if (current != null && line.StartsWith("-"))
                {
                    current.Bullets.Add(line.TrimStart('-').Trim());
                }
            }

            if (current != null) roles.Add(current);
            return roles;
        }

        public static string ParseSummary(string gptText)
        {
            var lines = gptText.Split('\n');
            int start = Array.FindIndex(lines, l => l.Trim().Equals("## SUMMARY", StringComparison.OrdinalIgnoreCase));
            if (start == -1) return "";

            var summaryLines = new List<string>();
            for (int i = start + 1; i < lines.Length; i++)
            {
                var line = lines[i].Trim();
                if (line.StartsWith("##")) break;
                if (!string.IsNullOrWhiteSpace(line))
                    summaryLines.Add(line);
            }

            return string.Join(" ", summaryLines);
        }

        public static List<string> ParseSkills(string gptText)
        {
            var lines = gptText.Split('\n');
            var skills = new List<string>();
            int start = Array.FindIndex(lines, l =>
                l.Trim().Equals("## CORE COMPETENCIES", StringComparison.OrdinalIgnoreCase) ||
                l.Trim().Equals("## TECHNICAL SKILLS", StringComparison.OrdinalIgnoreCase) ||
                l.Trim().Equals("## SKILLS", StringComparison.OrdinalIgnoreCase));

            if (start == -1)
            {
                return skills;
            }

            for (int i = start + 1; i < lines.Length; i++)
            {
                var line = lines[i].Trim();
                if (line.StartsWith("##")) break;
                if (!string.IsNullOrWhiteSpace(line))
                    skills.Add(line.TrimStart('-').Trim());
            }

            return skills;
        }
    }
}