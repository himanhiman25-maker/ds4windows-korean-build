using System;
using System.Globalization;
using System.Windows.Data;
using DS4WinWPF.Translations;
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace DS4WindowsTests;

[TestClass]
public sealed class KoreanPresentationTests
{
    [TestMethod]
    public void PresentationPreservesValuesAndEnglishFallback()
    {
        var previous = CultureInfo.CurrentUICulture;
        try
        {
            foreach (string culture in new[] { "ko", "ko-KR" })
            {
                CultureInfo.CurrentUICulture = CultureInfo.GetCultureInfo(culture);
                Assert.AreEqual("A 버튼", KoreanUi.Text("A Button"));
                Assert.AreEqual("작동 대기", KoreanUi.Text("Armed"));
                Assert.AreEqual("균형 잡힌 방아쇠", KoreanUi.Text("Balanced Weapon"));
                Assert.AreEqual("컨트롤러 2 연결 해제", KoreanUi.Text("Disconnect Controller 2"));
                Assert.AreEqual("시스템 오디오 · 기본 출력", KoreanUi.Text("System audio · default output"));
                Assert.AreEqual("게임에서 제공하는 고급 햅틱을 유지하면서 오디오 기반 피드백을 더합니다.", KoreanUi.Text("Mix adds audio-driven detail while preserving game-provided advanced haptics."));
                Assert.AreEqual("DS4Windows 버전 VIIPERRC4.6.7-ko.3", KoreanUi.Text("DS4Windows version VIIPERRC4.6.7-ko.3"));
                Assert.AreEqual("[프로필 편집 시간] 프로필 불러오기: 단계=126ms · 누적=136ms",
                    KoreanUi.Text("[ProfileEditorTiming] profile loaded: phase=126ms total=136ms"));
                Assert.AreEqual("VIIPER 준비 완료. VIIPER 도우미: 설치됨 · usbip-win2: 설치됨 · 서버: 실행 중.",
                    KoreanUi.Text("VIIPER ready. VIIPER helper: installed; usbip-win2: installed; server: running."));
                Assert.AreEqual("결합 가능한 미결합 Joy-Con 2: 왼쪽 0개, 오른쪽 0개.",
                    KoreanUi.Text("0 left and 0 right unmatched Joy-Con 2 connections available."));
                Assert.AreEqual("끝까지 당기면 대체 실행", KoreanUi.Text("Replace at full pull"));
                Assert.AreEqual("test-game  ·  앱", KoreanUi.Text("test-game  ·  App"));
                Assert.AreEqual("왼쪽 스틱 위", KoreanUi.Text("LS Up"));
                string diagnostic = @"Driver PID=1234 path=C:\Program Files\DS4Windows\VIIPER\viiper.exe code=0x0005";
                Assert.AreEqual(diagnostic, KoreanUi.Text(diagnostic));
                var converter = new KoreanDisplayExtension();
                Assert.AreEqual("중지", converter.Convert("Stop", typeof(string), null, CultureInfo.InvariantCulture));
                Assert.AreSame(Binding.DoNothing, converter.ConvertBack("중지", typeof(string), null, CultureInfo.InvariantCulture));
            }
            CultureInfo.CurrentUICulture = CultureInfo.GetCultureInfo("en");
            Assert.AreEqual("A Button", KoreanUi.Text("A Button"));
            Assert.AreEqual("Disconnect Controller 2", KoreanUi.Text("Disconnect Controller 2"));
        }
        finally { CultureInfo.CurrentUICulture = previous; }
    }
}
