"""Apply a source-only localization overlay to a pinned upstream checkout.

No installed application, user profile, driver or registry is touched.
"""
from pathlib import Path
import argparse, collections, hashlib, html, json, re, shutil, subprocess, sys
import xml.etree.ElementTree as ET

UPSTREAM_COMMIT = '080495de61ae8b6ada6b4252337838e8b22119b8'
ATTRS = ('Text','Content','Header','Title','ToolTip','Watermark','TextOn','TextOff','DisplayName')
PREFIX = '{kui:UiText '
XML_SPACE = '{http://www.w3.org/XML/1998/namespace}space'

def add_resource(tree, key, value):
    assert tree.getroot().find(f"data[@name='{key}']") is None, key
    node = ET.SubElement(tree.getroot(),'data',{'name':key,XML_SPACE:'preserve'})
    ET.SubElement(node,'value').text = value

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source',type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    bundle = Path(__file__).resolve().parent
    head = subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    if head != UPSTREAM_COMMIT: raise SystemExit('Unexpected upstream revision: '+head)
    if subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True).strip():
        raise SystemExit('Source checkout must be clean. Use a fresh pinned checkout.')
    mapping = json.loads((bundle/'data'/'ui-ko.json').read_text(encoding='utf-8'))
    for line in (bundle/'data/dynamic-ko.tsv').read_text(encoding='utf-8').splitlines():
        if '\t' in line:
            english,translated=line.split('\t',1)
            mapping[english]=translated
    if any(not isinstance(k,str) or not isinstance(v,str) for k,v in mapping.items()):
        raise SystemExit('Invalid translation mapping')
    app = source/'DS4Windows'
    neutral_path = app/'Translations'/'Strings.resx'
    neutral = ET.parse(neutral_path)
    korean = ET.parse(bundle/'data'/'Strings.ko.resx')
    english_by_key = {e.get('name'):e.findtext('value','') for e in neutral.findall('data')}
    korean_by_key = {e.get('name'):e.findtext('value','') for e in korean.findall('data')}
    keys = {}
    for english, translated in mapping.items():
        # Existing keys are reused only when both language values match.
        candidates = [k for k,v in english_by_key.items()
                      if v == english and korean_by_key.get(k) == translated]
        if candidates: key = candidates[0]
        else:
            key = 'CloudUi_' + hashlib.sha256(english.encode('utf-8')).hexdigest()[:16]
            add_resource(neutral,key,english)
            add_resource(korean,key,translated)
        keys[english] = key
    changed = collections.Counter()
    substitutions = []
    pattern = re.compile(r'<!--.*?-->|(?P<attr>\b(?:'+ '|'.join(ATTRS) +r'))="(?P<value>[^"]*)"',re.S)
    for path in sorted((app/'DS4Forms').rglob('*.xaml')):
        original = path.read_text(encoding='utf-8-sig')
        def replace(match):
            if match.group('attr') is None: return match.group(0)
            # XML normalizes literal whitespace before decoding character refs.
            value = html.unescape(re.sub(r'[\t\r\n]',' ',match.group('value')))
            if value not in keys or value.startswith('{'): return match.group(0)
            key=keys[value]
            relative=path.relative_to(source).as_posix()
            changed[relative]+=1
            substitutions.append({'file':relative,'attribute':match.group('attr'),'english':value,'key':key})
            return match.group('attr')+'="'+PREFIX+key+'}"'
        updated = pattern.sub(replace,original)
        if updated != original:
            if 'xmlns:kui=' not in updated:
                updated = re.sub(r'(<(?:\w+:)?\w+)\b',
                    r'\1 xmlns:kui="clr-namespace:DS4WinWPF.Translations"',updated,count=1)
            ET.fromstring(updated)  # syntax, entities and namespace validation
            path.write_text(updated,encoding='utf-8',newline='\n')

    # Binding formats need explicit nested resource expressions.
    formats = [
        (app/'DS4Forms'/'MainWindow.xaml','StringFormat={}{0} profiles','{0} profiles'),
        (app/'DS4Forms'/'Themes'/'BridgeShellStyles.xaml',"StringFormat='Profile: {0}'",'Profile: {0}'),
    ]
    for path,old,english in formats:
        text=path.read_text(encoding='utf-8')
        assert text.count(old)==1,(path,old)
        text=text.replace(old,'StringFormat='+PREFIX+keys[english]+'}')
        ET.fromstring(text)
        path.write_text(text,encoding='utf-8',newline='\n')

    # Localize only display text in these C# regions; control identifiers and
    # controller/driver protocol strings are deliberately not rewritten.
    main_path=app/'DS4Forms'/'MainWindow.xaml.cs'
    text=main_path.read_text(encoding='utf-8-sig')
    start=text.index('        private void NavigateProfileEditor(int navigationIndex)')
    end=text.index('        private void ProfilesListBox_SelectionChanged',start)
    region=text[start:end]
    def cs_expression(english):
        return 'DS4WinWPF.Translations.KoreanUi.Get('+json.dumps(english,ensure_ascii=False)+')'
    for english in sorted(keys,key=len,reverse=True):
        literal=json.dumps(english,ensure_ascii=False)
        region=region.replace(literal,cs_expression(english))
    text=text[:start]+region+text[end:]
    for english in ('No matching profiles','No profiles yet',
                    'Try a different profile name or clear the search.',
                    'Create or import a profile to get started.'):
        literal=json.dumps(english)
        assert literal in text,english
        text=text.replace(literal,cs_expression(english))
    main_path.write_text(text,encoding='utf-8',newline='\n')
    vm=app/'DS4Forms'/'ViewModels'/'MainWindowsViewModel.cs'
    text=vm.read_text(encoding='utf-8-sig')
    for english in ('No profile selected','Not connected','No emulated device','Generic profile'):
        literal=json.dumps(english)
        assert literal in text,english
        text=text.replace(literal,cs_expression(english))
    vm.write_text(text,encoding='utf-8',newline='\n')

    # Persist the chosen language immediately, as originally intended upstream.
    language_vm=app/'DS4Forms'/'ViewModels'/'LanguagePackViewModel.cs'
    text=language_vm.read_text(encoding='utf-8-sig')
    assert text.count('//Global.Save();')==1
    text=text.replace('//Global.Save();','Global.Save();')
    language_vm.write_text(text,encoding='utf-8',newline='\n')

    helper='''using System.Collections.Generic;
using System.Globalization;
namespace DS4WinWPF.Translations;
internal static partial class KoreanUi
{
    private static readonly Dictionary<string, string> Keys = new()
    {
'''
    for english,key in keys.items():
        helper += '        ['+json.dumps(english,ensure_ascii=False)+'] = '+json.dumps(key)+',\n'
    helper+='''    };
    internal static string Get(string english) =>
        Keys.TryGetValue(english, out string key)
            ? Strings.ResourceManager.GetString(key, CultureInfo.CurrentUICulture) ?? english
            : english;
}
'''
    (app/'Translations'/'KoreanUi.cs').write_text(helper,encoding='utf-8',newline='\n')
    sys.path.insert(0,str(bundle/'support'))
    from apply_dynamic import apply as apply_dynamic
    dynamic_patch_count=apply_dynamic(source,bundle)
    shutil.copyfile(bundle/'support'/'UiTextExtension.cs',app/'Translations'/'UiTextExtension.cs')
    for tree,path in ((neutral,neutral_path),(korean,app/'Translations'/'Strings.ko.resx')):
        tree.write(path,encoding='utf-8',xml_declaration=True)
    shutil.copyfile(bundle/'data'/'Resources.ko.resx',app/'Properties'/'Resources.ko.resx')

    # Existing layout tests retain their English-content assertions by resolving
    # our resource references to the neutral strings before comparing markup.
    # Structure, bindings, handlers and original assertions remain unchanged.
    tests=source/'DS4WindowsTests'
    shutil.copyfile(bundle/'support'/'LocalizedMarkup.cs',tests/'LocalizedMarkup.cs')
    for name in ('AppAudioSessionDiscoveryTests.cs','BindingWindowLiveInputLayoutTests.cs',
                 'FlickStickCalibrationLayoutTests.cs','ProfileMappingLiveInputTests.cs',
                 'Switch2ProfileSectionLayoutTests.cs','XboxImpulseProfileSettingsTests.cs',
                 'LogViewVirtualizationTests.cs'):
        path=tests/name
        text=path.read_text(encoding='utf-8-sig')
        text=text.replace('System.Xml.Linq.XDocument.Load(', 'LocalizedMarkup.Load(')
        text=text.replace('XDocument.Load(', 'LocalizedMarkup.Load(')
        path.write_text(text,encoding='utf-8',newline='\n')
    shutil.copyfile(bundle/'support'/'KoreanResourceTests.cs',tests/'KoreanResourceTests.cs')
    shutil.copyfile(bundle/'support'/'KoreanPresentationTests.cs',tests/'KoreanPresentationTests.cs')
    report={'upstream_commit':head,'ui_strings_available':len(keys),
            'xaml_attribute_replacements':sum(changed.values()),'changed_xaml':dict(changed),
            'resource_keys':keys,'substitutions':substitutions,
            'dynamic_presentation_patches':dynamic_patch_count,
            'known_limit':'External errors, third-party text and user-created names retain their original identifiers. Physical-controller acceptance remains required.'}
    (source/'korean-localization-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('resource_keys','substitutions')},ensure_ascii=False,indent=2))

if __name__=='__main__': main()
