using System;
using System.Globalization;
using System.Windows;
using System.Windows.Data;
using System.Windows.Markup;

namespace DS4WinWPF.Translations;

// Stateless, one-way formatting of read-only presentation bindings.
// It does not replace source properties or write localized text back to data.
public sealed class KoreanDisplayExtension : MarkupExtension, IValueConverter
{
    public override object ProvideValue(IServiceProvider serviceProvider) => this;
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture) =>
        value is string text ? KoreanUi.Text(text) : value;
    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture) => Binding.DoNothing;
}
