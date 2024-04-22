param (
    [Parameter(Mandatory=$false)]
    [int]$port = 6667
)

waitress-serve --listen=0.0.0.0:$port movie_eggpoker:create_app