using Models;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;

namespace Services
{
    public static class DocxInjector
    {
        public static void InjectSections(string docPath, string summaryText, List<string> skills, List<RoleBlock> roles)
        {
            using var doc = WordprocessingDocument.Open(docPath, true);
            var body = doc.MainDocumentPart.Document.Body;

            // ✅ Dump all paragraph text to file for inspection
            var dumpPath = Path.Combine(Path.GetDirectoryName(docPath) ?? "", "docx_paragraphs_dump.txt");
            File.WriteAllLines(dumpPath, body.Elements<Paragraph>().Select(p => p.InnerText ?? ""));
            Console.WriteLine($"📄 Dumped paragraph text to: {dumpPath}");

            var allParas = body.Elements<Paragraph>().ToList();

            // ✅ Inject SUMMARY
            InjectSummary(body, allParas, summaryText);

            // ✅ Inject SKILLS (CORE COMPETENCIES)
            InjectSkills(body, allParas, skills);

            // ✅ Inject EXPERIENCE
            InjectExperience(body, allParas, roles);

            doc.MainDocumentPart.Document.Save();
            Console.WriteLine($"📄 Saved to: {docPath}");
        }

        private static void InjectSummary(Body body, List<Paragraph> allParas, string summaryText)
        {
            int summaryIndex = FindSectionIndex(allParas, "SUMMARY");
            if (summaryIndex == -1)
            {
                Console.WriteLine("❌ Could not find SUMMARY section");
                return;
            }

            // Find the content paragraph and spacing paragraph after the SUMMARY header
            Paragraph? contentTemplate = null;
            Paragraph? spacingTemplate = null;
            for (int i = summaryIndex + 1; i < allParas.Count; i++)
            {
                var text = allParas[i].InnerText.Trim();
                if (!string.IsNullOrWhiteSpace(text) && 
                    !text.Equals("CORE COMPETENCIES", StringComparison.OrdinalIgnoreCase) &&
                    !text.Equals("TECHNICAL SKILLS", StringComparison.OrdinalIgnoreCase) &&
                    !text.Equals("PROFESSIONAL EXPERIENCE", StringComparison.OrdinalIgnoreCase))
                {
                    contentTemplate = allParas[i];
                    
                    // Look for spacing paragraph after content
                    if (i + 1 < allParas.Count && IsSpacingParagraph(allParas[i + 1]))
                    {
                        spacingTemplate = allParas[i + 1];
                    }
                    break;
                }
            }

            if (contentTemplate == null)
            {
                Console.WriteLine("❌ Could not find SUMMARY content template");
                return;
            }

            // Clone the template and replace text
            var summaryPara = (Paragraph)contentTemplate.CloneNode(true);
            ReplaceTextInParagraph(summaryPara, summaryText);

            // Remove old summary content including spacing
            var toRemove = CollectUntilNextSection(allParas, summaryIndex);
            foreach (var p in toRemove)
            {
                if (p.Parent != null) p.Remove();
            }

            // Insert new summary after header
            var refreshedHeader = body.Elements<Paragraph>().FirstOrDefault(p =>
                p.InnerText.Trim().Equals("SUMMARY", StringComparison.OrdinalIgnoreCase));

            if (refreshedHeader != null)
            {
                body.InsertAfter(summaryPara, refreshedHeader);
                
                // Add spacing paragraph using original template if available
                if (spacingTemplate != null)
                {
                    var spacingPara = (Paragraph)spacingTemplate.CloneNode(true);
                    body.InsertAfter(spacingPara, summaryPara);
                }
            }

            Console.WriteLine("✅ Injected SUMMARY with spacing");
        }

        private static void InjectSkills(Body body, List<Paragraph> allParas, List<string> skills)
        {
            var skillsHeader = allParas.FirstOrDefault(p =>
                p.InnerText.Trim().Equals("CORE COMPETENCIES", StringComparison.OrdinalIgnoreCase) ||
                p.InnerText.Trim().Equals("TECHNICAL SKILLS", StringComparison.OrdinalIgnoreCase));

            if (skillsHeader == null)
            {
                Console.WriteLine("❌ Could not find CORE COMPETENCIES or TECHNICAL SKILLS header");
                return;
            }

            // Find bullet template and spacing template from existing skills
            Paragraph? bulletTemplate = null;
            Paragraph? spacingTemplate = null;
            int headerIndex = allParas.IndexOf(skillsHeader);
            for (int i = headerIndex + 1; i < allParas.Count; i++)
            {
                var text = allParas[i].InnerText.Trim();
                if (text.Equals("PROFESSIONAL EXPERIENCE", StringComparison.OrdinalIgnoreCase) ||
                    text.Equals("PUBLICATIONS", StringComparison.OrdinalIgnoreCase) ||
                    text.Equals("EDUCATION", StringComparison.OrdinalIgnoreCase))
                    break;
                
                if (!string.IsNullOrWhiteSpace(text) && IsBulletParagraph(allParas[i]))
                {
                    bulletTemplate = allParas[i];
                }
                
                // Look for spacing paragraph after skills
                if (IsSpacingParagraph(allParas[i]))
                {
                    spacingTemplate = allParas[i];
                }
            }

            if (bulletTemplate == null)
            {
                Console.WriteLine("❌ Could not find bullet template for skills");
                return;
            }

            // Remove existing skills including spacing
            var toRemove = new List<Paragraph>();
            for (int i = headerIndex + 1; i < allParas.Count; i++)
            {
                var text = allParas[i].InnerText.Trim();
                if (text.Equals("PROFESSIONAL EXPERIENCE", StringComparison.OrdinalIgnoreCase))
                    break;
                
                toRemove.Add(allParas[i]);
            }

            foreach (var p in toRemove)
            {
                if (p.Parent != null) p.Remove();
            }

            // Inject new skills with preserved formatting
            var currentAnchor = skillsHeader;
            foreach (var skill in skills)
            {
                var skillPara = CloneStyledBullet(bulletTemplate, skill);
                body.InsertAfter(skillPara, currentAnchor);
                currentAnchor = skillPara; // Move anchor forward
            }

            // Add spacing paragraph using original template if available
            if (spacingTemplate != null)
            {
                var spacingPara = (Paragraph)spacingTemplate.CloneNode(true);
                body.InsertAfter(spacingPara, currentAnchor);
            }

            Console.WriteLine($"✅ Injected {skills.Count} SKILLS with spacing");
        }

        private static void InjectExperience(Body body, List<Paragraph> allParas, List<RoleBlock> roles)
        {
            var expHeader = allParas.FirstOrDefault(p =>
                p.InnerText.Trim().Equals("PROFESSIONAL EXPERIENCE", StringComparison.OrdinalIgnoreCase));

            if (expHeader == null)
            {
                Console.WriteLine("❌ Could not find PROFESSIONAL EXPERIENCE header");
                return;
            }

            // Find bullet template from existing experience
            Paragraph? bulletTemplate = null;
            int headerIndex = allParas.IndexOf(expHeader);
            for (int i = headerIndex + 1; i < allParas.Count; i++)
            {
                if (IsBulletParagraph(allParas[i]))
                {
                    bulletTemplate = allParas[i];
                    break;
                }
            }

            if (bulletTemplate == null)
            {
                Console.WriteLine("❌ Could not find bullet template for experience");
                return;
            }

            // Process each role
            foreach (var role in roles)
            {
                // Only search within the PROFESSIONAL EXPERIENCE section
                var expStartIndex = allParas.IndexOf(expHeader);
                if (expStartIndex == -1) continue;
                
                // Find the job title paragraph by matching both title and date
                var titlePara = allParas.Skip(expStartIndex + 1).FirstOrDefault(p => 
                {
                    var text = p.InnerText.Trim();
                    var index = allParas.IndexOf(p);
                    var nextPara = allParas.ElementAtOrDefault(index + 1);
                    var nextText = nextPara?.InnerText.Trim() ?? "";
                    
                    // Only search within experience section (stop at next major section)
                    if (text.Equals("PUBLICATIONS", StringComparison.OrdinalIgnoreCase) ||
                        text.Equals("EDUCATION", StringComparison.OrdinalIgnoreCase) ||
                        text.Equals("VOLUNTEERING", StringComparison.OrdinalIgnoreCase))
                        return false;
                    
                    // Check if this paragraph contains the job title and the next paragraph has the date
                    var titleMatch = !string.IsNullOrEmpty(role.Title) && text.Contains(role.Title.Split('|')[0].Trim(), StringComparison.OrdinalIgnoreCase);
                    var dateMatch = !string.IsNullOrEmpty(role.Date) && nextText.Contains(role.Date, StringComparison.OrdinalIgnoreCase);
                    
                    return titleMatch && dateMatch;
                });

                if (titlePara == null)
                {
                    Console.WriteLine($"❌ Job title not found in CV: {role.Title}");
                    continue;
                }

                int titleIndex = allParas.IndexOf(titlePara);
                if (titleIndex == -1 || titleIndex + 1 >= allParas.Count)
                {
                    Console.WriteLine($"❌ Invalid title index for: {role.Title}");
                    continue;
                }

                // Verify date paragraph
                var datePara = allParas[titleIndex + 1];
                if (!datePara.InnerText.Contains(role.Date))
                {
                    Console.WriteLine($"⚠️ Date mismatch for: {role.Title}. Expected: {role.Date}, Found: {datePara.InnerText}");
                    continue;
                }

                // Remove existing bullets for this role
                var bulletsToRemove = new List<Paragraph>();
                for (int i = titleIndex + 2; i < allParas.Count; i++)
                {
                    var para = allParas[i];
                    var text = para.InnerText.Trim();
                    
                    // Stop at next job title or section
                    if (text.StartsWith("Software") || text.StartsWith("Research") || 
                        text.Equals("PUBLICATIONS", StringComparison.OrdinalIgnoreCase) ||
                        text.Equals("EDUCATION", StringComparison.OrdinalIgnoreCase))
                        break;
                    
                    if (IsBulletParagraph(para))
                        bulletsToRemove.Add(para);
                    else if (!string.IsNullOrWhiteSpace(text))
                        break; // Stop at non-bullet content
                }

                foreach (var p in bulletsToRemove)
                {
                    if (p.Parent != null) p.Remove();
                }

                // Insert new bullets after date paragraph
                var refreshedDatePara = body.Elements<Paragraph>().FirstOrDefault(p =>
                    p.InnerText.Contains(role.Date));

                if (refreshedDatePara != null)
                {
                    var currentAnchor = refreshedDatePara;
                    foreach (var bullet in role.Bullets)
                    {
                        var bulletPara = CloneStyledBullet(bulletTemplate, bullet);
                        body.InsertAfter(bulletPara, currentAnchor);
                        currentAnchor = bulletPara; // Move anchor forward
                    }

                    Console.WriteLine($"✅ Injected {role.Bullets.Count} bullets for: {role.Title.Split('|')[0].Trim()}");
                }
            }
        }

        private static int FindSectionIndex(List<Paragraph> paragraphs, string title)
        {
            return paragraphs.FindIndex(p =>
                p.InnerText.Trim().Equals(title, StringComparison.OrdinalIgnoreCase));
        }

        private static List<Paragraph> CollectUntilNextSection(List<Paragraph> paragraphs, int startIndex)
        {
            var toRemove = new List<Paragraph>();
            for (int i = startIndex + 1; i < paragraphs.Count; i++)
            {
                var text = paragraphs[i].InnerText.Trim();
                if (text.Equals("CORE COMPETENCIES", StringComparison.OrdinalIgnoreCase) ||
                    text.Equals("TECHNICAL SKILLS", StringComparison.OrdinalIgnoreCase) ||
                    text.Equals("PROFESSIONAL EXPERIENCE", StringComparison.OrdinalIgnoreCase) ||
                    text.Equals("PUBLICATIONS", StringComparison.OrdinalIgnoreCase) ||
                    text.Equals("EDUCATION", StringComparison.OrdinalIgnoreCase))
                    break;
                
                // Remove all paragraphs including spacing - we'll add new spacing
                toRemove.Add(paragraphs[i]);
            }
            return toRemove;
        }

        private static bool IsBulletParagraph(Paragraph p)
        {
            // Check for both numbering properties and Symbol font bullets
            return p.Descendants<NumberingProperties>().Any() ||
                   p.Descendants<Run>().Any(r => 
                       r.Descendants<RunFonts>().Any(f => f.Ascii == "Symbol"));
        }

        private static bool IsSpacingParagraph(Paragraph p)
        {
            // Check if this is an empty paragraph (spacing paragraph)
            var text = p.InnerText.Trim();
            return string.IsNullOrWhiteSpace(text);
        }

        private static void ReplaceTextInParagraph(Paragraph paragraph, string newText)
        {
            // Find the first text element and replace it, preserve all formatting
            var firstText = paragraph.Descendants<Text>().FirstOrDefault();
            if (firstText != null)
            {
                firstText.Text = newText;
                
                // Remove any additional text elements to avoid duplication
                var additionalTexts = paragraph.Descendants<Text>().Skip(1).ToList();
                foreach (var text in additionalTexts)
                {
                    text.Remove();
                }
            }
        }

        private static Paragraph CloneStyledBullet(Paragraph template, string newText)
        {
            var clone = (Paragraph)template.CloneNode(true);
            ReplaceTextInParagraph(clone, newText);
            return clone;
        }

    }
}