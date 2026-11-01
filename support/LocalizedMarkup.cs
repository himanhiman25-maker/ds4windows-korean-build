using System;
using System.IO;
using System.Linq;
using System.Xml.Linq;

namespace DS4WindowsTests;

// Resolve new localization references to neutral text for existing layout
// assertions. This does not remove or skip any of the upstream assertions.
internal static class LocalizedMarkup
{
    internal static XDocument Load(string path)
    {
        XDocument document = XDocument.Load(path);
        const string prefix = "{lex:Loc DS4Windows:Strings:";
        var attributes = document.Descendants().Attributes()
            .Where(a => a.Value.StartsWith(prefix, StringComparison.Ordinal) &&
                        a.Value.EndsWith("}", StringComparison.Ordinal)).ToArray();
        if (attributes.Length == 0) return document;
        DirectoryInfo root = new FileInfo(path).Directory;
        while (root != null && !File.Exists(Path.Combine(root.FullName,
                   "DS4Windows", "Translations", "Strings.resx"))) root = root.Parent;
        if (root == null) throw new FileNotFoundException("Neutral resource source not found.");
        var resources = XDocument.Load(Path.Combine(root.FullName, "DS4Windows",
            "Translations", "Strings.resx")).Root.Elements("data")
            .ToDictionary(e => (string)e.Attribute("name"), e => (string)e.Element("value"));
        foreach (var attribute in attributes)
        {
            string key = attribute.Value.Substring(prefix.Length,
                attribute.Value.Length - prefix.Length - 1);
            attribute.Value = resources[key];
        }
        return document;
    }
}
