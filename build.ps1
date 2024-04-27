npx tailwindcss -i ./src/style.css -o ./movie_eggpoker/static/css/style_gen.css
Copy-Item ./node_modules/video.js/dist/video-js.css ./movie_eggpoker/static/css/video-js.css -Force
npm run build