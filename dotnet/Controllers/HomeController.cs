using Microsoft.AspNetCore.Mvc;

namespace DotnetApp.Controllers;

[ApiController]
[Route("")]
public class HomeController : ControllerBase
{
    private readonly IConfiguration _configuration;

    public HomeController(IConfiguration configuration)
    {
        _configuration = configuration;
    }

    [HttpGet]
    public IActionResult Get()
    {
        return Ok(new
        {
            message = "Hello from .NET Core!",
            environment = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") ?? "Production",
            hostname = Environment.MachineName,
            version = "1.0.0"
        });
    }

    [HttpGet("api/info")]
    public IActionResult GetInfo()
    {
        return Ok(new
        {
            app = "ASP.NET Core Web API",
            version = "1.0.0",
            dotnetVersion = Environment.Version.ToString()
        });
    }
}
