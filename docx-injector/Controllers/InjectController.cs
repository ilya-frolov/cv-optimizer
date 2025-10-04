using Microsoft.AspNetCore.Mvc;
using Services;

[ApiController]
[Route("inject")]
public class InjectController : ControllerBase
{
    [HttpPost]
    public IActionResult Inject([FromBody] string gptText)
    {
        string inputDocx = Path.GetFullPath("temp/uploaded_cv.docx");
        string outputDocx = Path.GetFullPath("temp/optimized_cv.docx");

        try
            {
                Console.WriteLine("📥 Received GPT text");
                var roles = GptParser.ParseRoles(gptText);
                var summaryText = GptParser.ParseSummary(gptText);
                var skillsList = GptParser.ParseSkills(gptText);

                Console.WriteLine($"📦 Parsed {roles.Count} roles");
                Console.WriteLine($"🧠 Summary: {summaryText}");
                Console.WriteLine($"🛠️ Skills: {skillsList.Count}");

                System.IO.File.Copy(inputDocx, outputDocx, true);

                DocxInjector.InjectSections(outputDocx, summaryText, skillsList, roles);

                return PhysicalFile(outputDocx, "application/vnd.openxmlformats-officedocument.wordprocessingml.document");
            }
            catch (Exception ex)
            {
                Console.WriteLine("❌ Injection failed: " + ex.Message);
                Console.WriteLine("🔍 StackTrace: " + ex.StackTrace);

                return StatusCode(500, $"Injection failed: {ex.Message}");
            }


    }
}