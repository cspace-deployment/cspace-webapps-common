/* eslint import/no-extraneous-dependencies: "off" */

const webpack = require('webpack');

const library = 'webappstuff';
/* const env = process.env.NODE_ENV;
 const isProduction = env === 'production'; */
const isProduction = true;

const config = {
    entry: {
      app: './client_modules/js/app.js',
      toolbox: './client_modules/js/toolbox-index.js'
    },
    output: {
        path: __dirname+ '/webpack_dist/',
        filename: '[name].bundle.js',
        library: library,
        libraryTarget: 'umd'
    },
    module: {
        loaders: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                loader: 'babel-loader',
            },
        ],
    },
    plugins: [
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery",
            "window.jQuery": "jquery",
            d3: 'd3'
        }),
    ],
    resolve: {
        extensions: ['.js', '.jsx'],
    },
};

if (isProduction) {
    config.plugins.push(
        new webpack.optimize.UglifyJsPlugin({
            compress: {
                warnings: false,
            },
            output: {
                comments: false,
            },
        })
    );
}

module.exports = config;
