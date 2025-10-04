using Microsoft.AspNetCore.Mvc.Formatters;
using System.Text;

public class PlainTextInputFormatter : TextInputFormatter
{
    public PlainTextInputFormatter()
    {
        SupportedMediaTypes.Add("text/plain");
        SupportedEncodings.Add(System.Text.Encoding.UTF8);
        SupportedEncodings.Add(System.Text.Encoding.Unicode);
    }

    protected override bool CanReadType(Type type)
    {
        return type == typeof(string);
    }

    public override async Task<InputFormatterResult> ReadRequestBodyAsync(InputFormatterContext context, Encoding encoding)
    {
        var request = context.HttpContext.Request;
        using var reader = new StreamReader(request.Body, encoding);
        var content = await reader.ReadToEndAsync();
        return await InputFormatterResult.SuccessAsync(content);
    }
}