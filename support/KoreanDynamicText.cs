using System;
using System.Collections.Concurrent;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace DS4WinWPF.Translations;

internal static partial class KoreanUi
{
    private sealed record Rule(Regex Pattern, string Key, int Count);
    private static readonly Regex Placeholder = new(@"\{(\d+)(?:[^{}]*)\}", RegexOptions.CultureInvariant);
    private static readonly Lazy<Rule[]> Rules = new(() => Keys
        .Where(item => Placeholder.IsMatch(item.Key))
        .OrderByDescending(item => item.Key.Length)
        .Select(item => CreateRule(item.Key, item.Value)).ToArray());
    private static readonly ConcurrentDictionary<string, string> DisplayCache = new();

    private static Rule CreateRule(string english, string key)
    {
        var pattern = new StringBuilder("\\A");
        int offset = 0, count = 0;
        var used = new System.Collections.Generic.HashSet<int>();
        foreach (Match placeholder in Placeholder.Matches(english))
        {
            pattern.Append(Regex.Escape(english.Substring(offset, placeholder.Index - offset)));
            int index = int.Parse(placeholder.Groups[1].Value, CultureInfo.InvariantCulture);
            pattern.Append(used.Add(index) ? $"(?<p{index}>.*?)" : $"\\k<p{index}>");
            count = Math.Max(count, index + 1);
            offset = placeholder.Index + placeholder.Length;
        }
        pattern.Append(Regex.Escape(english.Substring(offset))).Append("\\z");
        return new Rule(new Regex(pattern.ToString(), RegexOptions.CultureInvariant | RegexOptions.Singleline,
            TimeSpan.FromMilliseconds(100)), key, count);
    }

    // Called only at presentation boundaries. Stored profiles, enum values,
    // device identities and file logs are never changed by this method.
    internal static string Text(string english)
    {
        if (string.IsNullOrEmpty(english) || CultureInfo.CurrentUICulture.TwoLetterISOLanguageName != "ko")
            return english;
        if (DisplayCache.TryGetValue(english, out string cached)) return cached;
        string translated = Get(english);
        if (translated == english)
        {
            foreach (Rule rule in Rules.Value)
            {
                Match match;
                try { match = rule.Pattern.Match(english); }
                catch (RegexMatchTimeoutException) { continue; }
                if (!match.Success) continue;
                string format = Strings.ResourceManager.GetString(rule.Key, CultureInfo.CurrentUICulture);
                object[] arguments = Enumerable.Range(0, rule.Count)
                    .Select(index => (object)Get(match.Groups["p" + index].Value)).ToArray();
                try { translated = string.Format(CultureInfo.CurrentUICulture, format, arguments); }
                catch (FormatException) { translated = english; }
                break;
            }
        }
        // Composite status text may include a translated clause and several
        // identifiers. Handle the long combined VIIPER line before fragments.
        if (translated == english && english.Contains(" -> ", StringComparison.Ordinal))
            translated = string.Join(" → ", english.Split(" -> ").Select(Get));
        if (translated == english && english.Contains(", ", StringComparison.Ordinal))
            translated = string.Join(", ", english.Split(", ").Select(Get));
        if (DisplayCache.Count > 2048) DisplayCache.Clear();
        DisplayCache.TryAdd(english, translated);
        return translated;
    }
}
