
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');

module.exports = {
    entry: {
        search: './src/pages/search/search.js',
        header: './src/pages/layout/header/header.js',
        messages: './src/pages/messages/messages.js'
    },
    mode: 'development',
    output: {
        filename: 'static/js/[name].[contenthash].js',
        path: path.resolve(__dirname, 'dist'),
    },
    externals: {
        'VueBootstrapTypeahead': "VueBootstrapTypeahead",
    },
    optimization: {
        moduleIds: 'hashed',
        runtimeChunk: 'single',
        splitChunks: {
            cacheGroups: {
                vendor: {
                    test: /[\\/]node_modules[\\/]/,
                    name: 'vendors',
                    chunks: 'all',
                }
            }
        }
    },
    plugins: [
        new CleanWebpackPlugin({
            cleanOnceBeforeBuildPatterns:['**static/js/**', '!**templates/**', '!**static/css**']
        }),
        
        new HtmlWebpackPlugin({
            title: 'Search',
            filename: "templates/index.html",
            template: "src/templates/index.html",
            chunks: ['search'],
            inject: false,
        }),
        new HtmlWebpackPlugin({
            title: 'Header',
            filename: "templates/layout/components/header.html",
            template: "src/templates/header.html",
            chunks: ['header'],
        }),
        new HtmlWebpackPlugin({
            title: 'Messages',
            filename: "templates/messages.html",
            template: "src/templates/messages.html",
            chunks: ['messages'],
            inject: false,
        }),
        new HtmlWebpackPlugin({
            title: 'Imports',
            filename: "templates/layout/components/imports.html",
            template: "src/templates/imports.html",
            chunks: ['vendors', 'runtime'],
        })
    ],
    resolve: {
        alias: {
          'vue': 'vue/dist/vue.esm.js' // 'vue/dist/vue.common.js' for webpack 1
        }
    }

}