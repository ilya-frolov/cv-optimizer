using System.Text.Json;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;

class Program
{
    static void Main(string[] args)
    {
        string jsonPath = "temp/injection.json";
        string docxPath = "templates/reference.docx";
        string outputPath = "temp/optimized_cv.docx";

        var json = File.ReadAllText(jsonPath);
        var data = JsonSerializer.Deserialize<Dictionary<string, string>>(json);

        File.Copy(docxPath, outputPath, true);

        using var doc = WordprocessingDocument.Open(outputPath, true);
        var body = doc.MainDocumentPart.Document.Body;

        foreach (var entry in data)
        {
            var bookmark = body.Descendants<BookmarkStart>()
                               .FirstOrDefault(b => b.Name == entry.Key);
            if (bookmark != null)
            {
                var run = new Run(new Text(entry.Value));
                bookmark.Parent.InsertAfter(run, bookmark);
            }
        }

        doc.MainDocumentPart.Document.Save();
        Console.WriteLine("✅ Injection complete.");
    }
}