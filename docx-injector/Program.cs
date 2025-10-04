using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

var builder = WebApplication.CreateBuilder(args);

// Add services
builder.Services.AddControllers(options =>
{
    options.InputFormatters.Insert(0, new PlainTextInputFormatter());
});

var app = builder.Build();

// Configure middleware
app.UseRouting();
app.UseAuthorization(); // Optional

app.MapControllers();

Console.WriteLine("✅ ASP.NET is running");
app.Run();