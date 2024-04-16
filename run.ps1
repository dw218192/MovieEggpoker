param(
    [string]$app = "movie-eggpoker",
    #flag to run in debug mode
    [switch]$debug = $false
)

if ($debug) {
    Write-Output "Running in debug mode..."
    flask --app $app run --debug
} else {
    flask --app $app run
}