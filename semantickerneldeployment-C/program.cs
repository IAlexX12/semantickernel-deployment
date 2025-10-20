using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.SemanticKernel;
using Microsoft.SemanticKernel.ChatCompletion;

var builder = WebApplication.CreateBuilder(args);

// Configuración de Semantic Kernel antes de Build()
var apiKey = Environment.GetEnvironmentVariable("OPENAI_API_KEY");
var deploymentName = "gpt-4o-mini";
var endpoint = "https://aleja-mghyt28b-eastus2.openai.azure.com/";

builder.Services.AddSingleton<Kernel>(sp =>
{
    return Kernel.CreateBuilder()
        .AddAzureOpenAIChatCompletion(deploymentName: deploymentName, endpoint: endpoint, apiKey: apiKey)
        .Build();
});

builder.Services.AddSingleton(sp =>
    sp.GetRequiredService<Kernel>().GetRequiredService<IChatCompletionService>()
);

var app = builder.Build();

app.MapPost("/chat", async (HttpRequest request, Kernel kernel, IChatCompletionService chat) =>
{
    var data = await request.ReadFromJsonAsync<ChatRequest>();
    if (data == null || string.IsNullOrWhiteSpace(data.Message))
        return Results.BadRequest(new { error = "Campo 'message' requerido" });

    var history = new ChatHistory();
    history.AddUserMessage(data.Message);

    string responseText = "";
    await foreach (var chunk in chat.GetStreamingChatMessageContentsAsync(history))
    {
        responseText += chunk.Content;
    }

    return Results.Ok(new { reply = responseText });
});

app.Urls.Add("http://0.0.0.0:80");
app.Run();

record ChatRequest(string Message);
