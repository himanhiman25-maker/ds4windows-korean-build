using System;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Resources;
using System.Xml.Linq;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace DS4WindowsTests;

[TestClass]
public sealed class KoreanResourceTests
{
    [TestMethod]
    public void KoreanAndRegionalFallbackLoadEveryTranslatedString()
    {
        DirectoryInfo root = new(AppContext.BaseDirectory);
        while (root != null && !File.Exists(Path.Combine(root.FullName,
                   "DS4Windows", "Translations", "Strings.ko.resx"))) root = root.Parent;
        Assert.IsNotNull(root, "Find the production Korean resource source.");
        var assembly = typeof(DS4WinWPF.DS4Forms.MainWindow).Assembly;
        int checkedCount = 0;
        foreach (var spec in new[] { ("Translations", "Strings"), ("Properties", "Resources") })
        {
            var manager = new ResourceManager("DS4WinWPF." + spec.Item1 + "." + spec.Item2, assembly);
            var source = XDocument.Load(Path.Combine(root.FullName, "DS4Windows",
                spec.Item1, spec.Item2 + ".ko.resx"));
            foreach (var item in source.Root.Elements("data"))
            {
                string key = (string)item.Attribute("name");
                string expected = ((string)item.Element("value")).Replace("\r\n", "\n");
                foreach (string culture in new[] { "ko", "ko-KR" })
                    Assert.AreEqual(expected, manager.GetString(key,
                        CultureInfo.GetCultureInfo(culture))?.Replace("\r\n", "\n"), culture + ":" + key);
                checkedCount++;
            }
        }
        Assert.IsTrue(checkedCount > 1000, "Include the base pack and newly connected UI text.");
    }
}
