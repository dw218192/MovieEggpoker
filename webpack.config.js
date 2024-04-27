const path = require('path');
console.log(require.resolve('video.js'));
module.exports = {
  entry: './src/front_end.js', // Assuming your main JS file
  output: {
    filename: 'script.js',
    path: path.resolve(__dirname, 'movie_eggpoker/static/js'),
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
  resolve: {
    modules: [path.resolve(__dirname, 'node_modules'), 'node_modules'],
    extensions: ['.js', '.json', '.css'],
    alias: {
      'videojs' : require.resolve('video.js'),
    }
  },
  optimization: {
    minimize: process.env.NODE_ENV !== 'debug',
  },
};
