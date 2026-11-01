"""Reviewed presentation-only extensions for Korean build ko.3."""
from pathlib import Path
import json, re, shutil

CALL = 'DS4WinWPF.Translations.KoreanUi.Text'

def string_end(text, pos):
    # C# normal/verbatim/interpolated strings, including quotes inside holes.
    quote = pos
    while text[quote] != '"': quote += 1
    prefix = text[pos:quote]
    verbatim = '@' in prefix
    interpolated = '$' in prefix
    i = quote + 1
    depth = 0
    while i < len(text):
        c = text[i]
        if not verbatim and c == '\\': i += 2; continue
        if interpolated and c == '{':
            if depth == 0 and text[i:i+2] == '{{': i += 2; continue
            depth += 1; i += 1; continue
        if interpolated and c == '}' and depth:
            depth -= 1; i += 1; continue
        if c == '"':
            if depth:
                i = string_end(text, i); continue
            if verbatim and text[i:i+2] == '""': i += 2; continue
            return i + 1
        i += 1
    raise ValueError('Unclosed C# string')

def expression_end(text, start):
    i, depth = start, 0
    while i < len(text):
        c = text[i]
        if c == '"' or c in '$@' and text[i:i+2] in ('$"','@"') or text[i:i+3] in ('$@"','@$"'):
            i = string_end(text,i); continue
        if c in '([{': depth += 1
        elif c in ')]}':
            if depth == 0: return i
            depth -= 1
        elif c in ';,' and depth == 0: return i
        i += 1
    raise ValueError('Unclosed expression')

def apply(source, bundle):
    patches = []
    app = source/'DS4Windows'
    def replace(relative, old, new, required=True):
        path=source/relative
        text=path.read_text(encoding='utf-8-sig')
        original=text
        count=text.count(old)
        if required and not count: raise ValueError((relative,old))
        if not count: return
        text=text.replace(old,new)
        path.write_text(text,encoding='utf-8',newline='\n')
        patches.append({'file':relative,'old':old,'new':new,'count':count})

    ui_files = ['DS4Forms/TriggerLabControl.xaml.cs','DS4Forms/AudioHapticsControl.xaml.cs',
                'DS4Forms/MainWindow.xaml.cs','DS4Forms/ProfileEditor.xaml.cs',
                'DS4Forms/ViewModels/TrayIconViewModel.cs']
    # Translate complete values at display assignments, not their source data.
    for name in ui_files:
        relative='DS4Windows/'+name
        path=source/relative
        text=path.read_text(encoding='utf-8-sig')
        original=text
        matches=[]
        for match in re.finditer(r'\b(?P<property>Text|Content|Header|ToolTip)\s*=\s*(?!=)',text):
            line=text[text.rfind('\n',0,match.start())+1:match.start()]
            if line.lstrip().startswith('//'): continue
            start=match.end(); end=expression_end(text,start)
            expr=text[start:end].rstrip()
            if not expr or expr in ('""','string.Empty') or CALL in expr or expr.startswith(('new ','FindResource(','TryFindResource(','glyph','initial')): continue
            if 'profileNameTxt.' in line: continue
            if match.group('property')!='Text' and '"' not in expr and '.ActionLabel(' not in expr and expr not in ('label','text','tooltip','selected.Description','mode.Description','choice.Description','runtime.Message','ui.FullPullMapping.MappingName'): continue
            # These are visual objects, not strings.
            if 'Style' in expr or 'Brush' in expr or 'FontFamily' in expr: continue
            matches.append((start,start+len(expr),expr))
        for start,end,expr in reversed(matches):
            new=CALL+'('+expr+')'
            text=text[:start]+new+text[end:]
        if matches: replace(relative,original,text)

    # Only display literals in these small view models are eligible here.
    dynamic={}
    for line in (bundle/'data/dynamic-ko.tsv').read_text(encoding='utf-8').splitlines():
        if '\t' in line:
            en,ko=line.split('\t',1); dynamic[en]=ko
    for name in ('DS4Forms/ViewModels/ControllerUiCapabilityPolicy.cs',
                 'DS4Forms/ViewModels/Switch2AimSetupViewModel.cs',
                 'DS4Forms/TriggerLabControl.xaml.cs'):
        relative='DS4Windows/'+name
        path=source/relative; text=path.read_text(encoding='utf-8'); original=text
        matches=[]; i=0
        while i<len(text):
            if text[i:i+2]=='//':
                i=text.find('\n',i)
                if i<0: break
            elif text[i:i+2]=='/*':
                i=text.index('*/',i)+2
            elif text[i]=='"' or text[i:i+2] in ('$"','@"') or text[i:i+3] in ('$@"','@$"'):
                end=string_end(text,i); literal=text[i:end]
                if literal.startswith('"'):
                    try: english=json.loads(literal)
                    except ValueError: english=None
                    if english in dynamic and '{' not in english and english not in ('Start','Wall','Force','are','is','installed','missing','running','not running') and not text[max(0,i-5):i].endswith(('Text(','Get(')):
                        matches.append((i,end,literal))
                i=end
            else: i+=1
        for start,end,literal in reversed(matches):
            text=text[:start]+CALL+'('+literal+')'+text[end:]
        if matches: replace(relative,original,text)

    t='DS4Windows/DS4Forms/TriggerLabControl.xaml.cs'
    replace(t,'Name = preset.Name,','Name = '+CALL+'(preset.Name),')
    replace('DS4Windows/DS4Forms/ViewModels/TrayIconViewModel.cs','changeServiceItem.Header = temp;','changeServiceItem.Header = '+CALL+'(temp);')
    replace('DS4Windows/DS4Forms/ProfileEditor.xaml.cs',
        'physicalControlName ?? mapped.ControlName',CALL+'(physicalControlName ?? mapped.ControlName)')
    replace('DS4Windows/DS4Forms/MainWindow.xaml.cs','Label = label;','Label = '+CALL+'(label);')
    replace('DS4Windows/DS4Forms/MainWindow.xaml.cs','Label = candidate.Label;','Label = '+CALL+'(candidate.Label);')
    # Built-in preset names are translated in the UI; custom names remain raw.
    a='DS4Windows/DS4Forms/AudioHapticsControl.xaml.cs'
    replace(a,'public string DisplayName { get; init; }','public string DisplayName { get; init; }\n            public string LocalizedDisplayName => '+CALL+'(DisplayName);')

    m='DS4Windows/DS4Forms/ViewModels/MappingListViewModel.cs'
    for field in ('controlName','mappingName','shiftMappingName'):
        replace(m,'get => '+field+';','get => '+CALL+'('+field+');')
    w='DS4Windows/DS4Forms/ViewModels/MainWindowsViewModel.cs'
    replace(w,'"No physical controller selected"',CALL+'("No physical controller selected")')
    # Leave ActionName (the storage/export identity) intact and add a UI-only name.
    s='DS4Windows/DS4Forms/ViewModels/SpecialActionsListViewModel.cs'
    replace(s,'public event EventHandler ActionNameChanged;',
        'public string LocalizedActionName => specialAction.typeID == SpecialAction.ActionTypeId.DisconnectBT &&\n'+
        '            specialAction.name == "Disconnect Controller" ? '+CALL+'(specialAction.name) : specialAction.name;\n'+
        '        public event EventHandler ActionNameChanged;')
    replace(s,'public string Controls { get => specialAction.controls.Replace("/", ", "); }',
        'public string Controls { get => '+CALL+'(specialAction.controls.Replace("/", ", ")); }')

    # XAML uses a stateless display converter. Original binding paths/data remain.
    for relative in ('DS4Windows/DS4Forms/MainWindow.xaml',):
        for old in ('{Binding Message}','{Binding Path=Message}'):
            replace(relative,old,old[:-1]+', Converter={kui:KoreanDisplay}}')
    p='DS4Windows/DS4Forms/ProfileEditor.xaml'
    replace(p,'{Binding ActionName}','{Binding LocalizedActionName}')
    replace(p,'StringFormat=Max Light {0:N2}%',
        "StringFormat={kui:UiText CloudUi_"+__import__('hashlib').sha256(b'Max Light {0:N2}%').hexdigest()[:16]+'}')
    replace('DS4Windows/DS4Forms/AudioHapticsControl.xaml','DisplayMemberPath="DisplayName"','DisplayMemberPath="LocalizedDisplayName"')
    replace('DS4Windows/DS4Forms/LogMessageDisplay.xaml.cs',
        '            Regex urlReg =', '            message = '+CALL+'(message);\n            Regex urlReg =')
    for file in ('KoreanDynamicText.cs','KoreanDisplayExtension.cs'):
        shutil.copyfile(bundle/'support'/file,app/'Translations'/file)
    (source/'korean-dynamic-patches.json').write_text(json.dumps(patches,ensure_ascii=False,indent=2),encoding='utf-8')
    return len(patches)
