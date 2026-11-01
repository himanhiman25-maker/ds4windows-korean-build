using System;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Resources;
using System.Xml.Linq;
using System.Threading;
using System.Windows.Controls;
using System.Windows.Markup;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace DS4WindowsTests;

[TestClass]
public sealed class KoreanResourceTests
{
    [TestMethod]
    public void NewUiTextCanRenderOnIndependentStaThreadsInBothLanguages()
    {
        // Guard against localization waiting on a previous thread's dispatcher.
        // Exercise two fresh, sequential STA lifetimes instead.
        foreach (string culture in new[] { "ko-KR", "en" })
        {
            Exception failure = null;
            var thread = new Thread(() =>
            {
                try
                {
                    CultureInfo.CurrentUICulture = CultureInfo.GetCultureInfo(culture);
                    // Use the production key selected for the Overview label.
                    var key = "CloudUi_" + Convert.ToHexString(
                        System.Security.Cryptography.SHA256.HashData(
                            System.Text.Encoding.UTF8.GetBytes("Overview")))
                        .Substring(0, 16).ToLowerInvariant();
                    var markup = "<TextBlock xmlns=\"http://schemas.microsoft.com/winfx/2006/xaml/presentation\" " +
                        "xmlns:kui=\"clr-namespace:DS4WinWPF.Translations;assembly=DS4Windows\" " +
                        "Text=\"{kui:UiText " + key + "}\" />";
                    var control = (TextBlock)XamlReader.Parse(markup);
                    Assert.AreEqual(culture == "ko-KR" ? "개요" : "Overview", control.Text);
                }
                catch (Exception ex) { failure = ex; }
            }) { IsBackground = true };
            thread.SetApartmentState(ApartmentState.STA);
            thread.Start();
            Assert.IsTrue(thread.Join(TimeSpan.FromSeconds(10)), "Text rendering must not wait on a dead dispatcher.");
            if (failure != null) Assert.Fail(failure.ToString());
        }
    }

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
