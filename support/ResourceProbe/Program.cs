using System.Globalization;
using System.Reflection;
using System.Resources;
using System.Runtime.Loader;
using System.Text.Json;
using System.Xml.Linq;

// Read resources only. Never construct App, ControlService or a controller.
string source = Path.GetFullPath(args[0]);
Assembly app = AssemblyLoadContext.Default.LoadFromAssemblyPath(
    Path.Combine(AppContext.BaseDirectory, "DS4Windows.dll"));
int count = 0;
foreach (var spec in new[] { ("Translations", "Strings"), ("Properties", "Resources") })
{
    var manager = new ResourceManager("DS4WinWPF." + spec.Item1 + "." + spec.Item2, app);
    var document = XDocument.Load(Path.Combine(source, "DS4Windows",
        spec.Item1, spec.Item2 + ".ko.resx"));
    foreach (var item in document.Root!.Elements("data"))
    {
        string key = (string)item.Attribute("name")!;
        string expected = ((string)item.Element("value")!).Replace("\r\n", "\n");
        foreach (string culture in new[] { "ko", "ko-KR" })
            if (manager.GetString(key, CultureInfo.GetCultureInfo(culture))?.Replace("\r\n", "\n") != expected)
                throw new InvalidOperationException(culture + ": " + spec.Item2 + ": " + key);
        count++;
    }
}
var satellite = app.GetSatelliteAssembly(CultureInfo.GetCultureInfo("ko"));
Console.WriteLine(JsonSerializer.Serialize(new {
    Passed = true, Entries = count, Cultures = new[] { "ko", "ko-KR" },
    Satellite = satellite.Location, AppEntryPointInvoked = false
}));
