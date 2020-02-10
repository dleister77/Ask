
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');

module.exports = {
    entry: {
        search: './src/pages/search/search.js',
        header: './src/pages/layout/header/header.js',
    },
    mode: 'development',
    output: {
        filename: 'js/[name].[contenthash].js',
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
            cleanOnceBeforeBuildPatterns:['**js/**', '!**templates/**']
        }),
        
        new HtmlWebpackPlugin({
            title: 'Search',
            filename: "templates/index.html",
            template: "src/templates/index.html",
            chunks: ['search', 'vendors', 'runtime'],
            inject: false,
        }),
        new HtmlWebpackPlugin({
            title: 'Header',
            filename: "templates/header.html",
            template: "src/templates/header.html",
            chunks: ['header'],
        }),
    ],
    resolve: {
        alias: {
          'vue': 'vue/dist/vue.esm.js' // 'vue/dist/vue.common.js' for webpack 1
        }
    }

}