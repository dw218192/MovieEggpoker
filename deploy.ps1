param (
    [Parameter(Mandatory=$false)]
    [int]$port = 6666,
    [switch]$dbg
)

if ($dbg) {
    Write-Host "Debug mode enabled"
    $env:FLASK_DEBUG = 1
}

waitress-serve --listen=localhost:$port --call movie_eggpoker:create_app