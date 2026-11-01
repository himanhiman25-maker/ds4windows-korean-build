using System;
using System.Globalization;
using System.Windows.Markup;

namespace DS4WinWPF.Translations;

// Language changes already require an application restart. Resolve new UI text
// once from ResourceManager, without registering with a shared WPF dispatcher.
// This also permits independent STA windows to be created and destroyed safely.
[MarkupExtensionReturnType(typeof(string))]
public sealed class UiTextExtension : MarkupExtension
{
    public UiTextExtension() { }
    public UiTextExtension(string key) => Key = key;

    public string Key { get; set; }

    public override object ProvideValue(IServiceProvider serviceProvider) =>
        string.IsNullOrEmpty(Key) ? string.Empty :
        Strings.ResourceManager.GetString(Key, CultureInfo.CurrentUICulture) ?? Key;
}
