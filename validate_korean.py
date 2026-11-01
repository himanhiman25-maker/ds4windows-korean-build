"""Check resource coverage and preserve non-text XAML behavior before building."""
from pathlib import Path
import json, re, subprocess, sys
import xml.etree.ElementTree as ET

source=Path(sys.argv[1]).resolve()
report=json.loads((source/'korean-localization-report.json').read_text(encoding='utf-8'))
prefix='{kui:UiText '
neutral=ET.parse(source/'DS4Windows'/'Translations'/'Strings.resx')
values={e.get('name'):e.findtext('value','') for e in neutral.findall('data')}
total=0
for folder,name in [('Translations','Strings'),('Properties','Resources')]:
    base=ET.parse(source/'DS4Windows'/folder/(name+'.resx'))
    korean=ET.parse(source/'DS4Windows'/folder/(name+'.ko.resx'))
    en={e.get('name'):e.findtext('value','') for e in base.findall('data')}
    seen=set()
    for e in korean.findall('data'):
        key=e.get('name'); ko=e.findtext('value','')
        assert key not in seen,'Duplicate key: '+key
        seen.add(key)
        assert key in en,'Unknown Korean key: '+key
        pattern=r'\{\d+(?:[^{}]*)\}|\*(?:number|Mac address|button|program|profile|Profile name|action)\*'
        assert sorted(re.findall(pattern,en[key]))==sorted(re.findall(pattern,ko)),key
        total+=1
checked_nodes=0
for relative in report['changed_xaml']:
    original=subprocess.check_output(['git','-C',str(source),'show',report['upstream_commit']+':'+relative])
    old=ET.fromstring(original)
    new=ET.parse(source/relative).getroot()
    old_nodes=list(old.iter()); new_nodes=list(new.iter())
    assert len(old_nodes)==len(new_nodes),relative
    for a,b in zip(old_nodes,new_nodes):
        assert a.tag==b.tag,(relative,a.tag,b.tag)
        assert set(a.attrib)==set(b.attrib),(relative,a.tag,'attribute set changed')
        for key,expected in a.attrib.items():
            actual=b.attrib[key]
            if actual.startswith(prefix) and actual.endswith('}'):
                resource_key=actual[len(prefix):-1]
                assert values[resource_key]==expected,(relative,key,expected)
            elif key=='Text' and 'StringFormat={kui:UiText ' in actual:
                # Only the two reviewed display formats are permitted.
                assert (relative.endswith('MainWindow.xaml') and 'Path=Items.Count' in expected) or (
                    relative.endswith('BridgeShellStyles.xaml') and 'SelectedProfile' in expected)
            else:
                assert actual==expected,(relative,key,expected,actual)
        # Preserve direct content, named controls, handlers, tags and all bindings.
        assert (a.text or '').strip()==(b.text or '').strip(),relative
        checked_nodes+=1
assert report['xaml_attribute_replacements']>900
assert total>1000
assert 'Global.Save();' in (source/'DS4Windows'/'DS4Forms'/'ViewModels'/'LanguagePackViewModel.cs').read_text(encoding='utf-8')
def original_text(relative):
    return subprocess.check_output(['git','-C',str(source),'show',report['upstream_commit']+':'+relative]).decode('utf-8-sig').replace('\r\n','\n')
for relative in ('DS4Windows/DS4Forms/MainWindow.xaml.cs',
                 'DS4Windows/DS4Forms/ViewModels/MainWindowsViewModel.cs'):
    modified=(source/relative).read_text(encoding='utf-8-sig')
    restored=re.sub(r'DS4WinWPF\.Translations\.KoreanUi\.Get\(("(?:\\.|[^"\\])*")\)',r'\1',modified)
    assert restored==original_text(relative),'Non-display C# changed: '+relative
relative='DS4Windows/DS4Forms/ViewModels/LanguagePackViewModel.cs'
assert (source/relative).read_text(encoding='utf-8-sig').replace('                    Global.Save();','                    //Global.Save();')==original_text(relative)
for name in ('AppAudioSessionDiscoveryTests.cs','BindingWindowLiveInputLayoutTests.cs',
             'FlickStickCalibrationLayoutTests.cs','ProfileMappingLiveInputTests.cs',
             'Switch2ProfileSectionLayoutTests.cs','XboxImpulseProfileSettingsTests.cs',
             'LogViewVirtualizationTests.cs'):
    relative='DS4WindowsTests/'+name
    before=original_text(relative)
    expected=before.replace('System.Xml.Linq.XDocument.Load(', 'LocalizedMarkup.Load(').replace('XDocument.Load(', 'LocalizedMarkup.Load(')
    assert expected==(source/relative).read_text(encoding='utf-8-sig'),relative
result={'translated_resource_entries':total,'reviewed_xaml_nodes':checked_nodes,
        'xaml_attribute_replacements':report['xaml_attribute_replacements'],
        'behavioral_markup_preserved':True,'non_display_csharp_preserved':True,
        'existing_test_assertions_preserved':True,'windows_compilation':'not performed by this check'}
(source/'korean-static-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
