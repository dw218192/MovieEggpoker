param (
    [Parameter(Mandatory=$false)]
    [int]$port = 8888,
    [switch]$dbg
)

if ($dbg) {
    Write-Host "Debug mode enabled"
    $env:FLASK_DEBUG = 1
    $process = Start-Process -PassThru -NoNewWindow powershell.exe -ArgumentList "-NoExit -Command npx tailwindcss -i ./src/style.css -o ./movie_eggpoker/static/css/style_gen.css --watch"
}

try {
    waitress-serve --listen=localhost:$port --call movie_eggpoker:create_app
} finally {
    Write-Host "Cleaning up..."
    if ($dbg -and !$process.HasExited) {
        $process | Stop-Process -Force
    }
}
