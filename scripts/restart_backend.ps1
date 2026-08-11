# Compile FileUploadUtils and restart backend
$ErrorActionPreference = 'Stop'
$demo = 'C:\Users\rbh\Downloads\hotel-1.2\demo'
$java = 'D:\java\Java\bin\javac.exe'

$proc = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'java.exe' -and $_.CommandLine -like '*com.example.demo.DemoApplication*' }
if (-not $proc) { Write-Error 'backend process not found'; exit 1 }
$cmdline = $proc.CommandLine
Write-Host ("old PID: " + $proc.ProcessId)

# extract classpath
$m = [regex]::Match($cmdline, '-cp "([^"]+)"')
if (-not $m.Success) { Write-Error 'cannot extract classpath'; exit 1 }
$cp = $m.Groups[1].Value

# compile
$src = Join-Path $demo 'src\main\java\com\example\demo\common\FileUploadUtils.java'
& $java -encoding UTF-8 -cp $cp -d (Join-Path $demo 'target\classes') $src
if ($LASTEXITCODE -ne 0) { Write-Error 'javac failed'; exit 1 }
Write-Host 'compile OK'

# restart
Stop-Process -Id $proc.ProcessId -Force
Start-Sleep -Seconds 3

$cmdFile = Join-Path $demo 'start_backend.cmd'
$cmdContent = '@echo off' + [char]13 + [char]10 + 'cd /d "' + $demo + '"' + [char]13 + [char]10 + $cmdline + ' > backend.log 2>&1' + [char]13 + [char]10
Set-Content -Path $cmdFile -Value $cmdContent -Encoding ASCII
Start-Process -FilePath $cmdFile -WindowStyle Hidden
Write-Host 'backend starting...'

# wait for 8080
for ($i = 0; $i -lt 40; $i++) {
    Start-Sleep -Seconds 1
    try {
        $r = Invoke-WebRequest -Uri 'http://localhost:8080/api/banner/list' -UseBasicParsing -TimeoutSec 3
        if ($r.StatusCode -eq 200) { Write-Host 'backend ready'; break }
    } catch {}
}
$new = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'java.exe' -and $_.CommandLine -like '*com.example.demo.DemoApplication*' }
Write-Host ("new PID: " + $new.ProcessId)
