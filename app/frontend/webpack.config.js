
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const {CleanWebpackPlugin} = require('clean-webpack-plugin');

module.exports = {
    entry: {
        search: './src/pages/search/search.js',
        header: './src/pages/layout/header/header.js',
        messages: './src/pages/messages/messages.js',
        providerAdd: './src/pages/provider/providerAdd.js',
        groupSearch: './src/pages/group/groupSearch.js',
        friendAdd: './src/pages/friend/friendAdd.js',
        review: './src/pages/review/review.js',
        register: './src/pages/register/register.js'
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
            filename: "templates/index.html",
            template: "src/templates/index.html",
            chunks: ['search'],
            inject: false,
        }),
        new HtmlWebpackPlugin({
            filename: "templates/layout/components/header.html",
            template: "src/templates/header.html",
            chunks: ['header'],
        }),
        new HtmlWebpackPlugin({
            filename: "templates/messages.html",
            template: "src/templates/messages.html",
            chunks: ['messages'],
            inject: false,
        }),
        new HtmlWebpackPlugin({
            filename: "templates/layout/components/imports.html",
            template: "src/templates/imports.html",
            chunks: ['vendors', 'runtime'],
        }),
        new HtmlWebpackPlugin({
            filename: "templates/provideradd.html",
            template: "src/templates/provideradd.html",
            chunks: ["providerAdd"],
            inject: false,
        }),
        new HtmlWebpackPlugin({
            filename: "templates/relationship/groupSearch.html",
            template: "src/templates/groupSearch.html",
            chunks: ["groupSearch"],
            inject: false,
        }),
        new HtmlWebpackPlugin({
            filename: "templates/relationship/network_friends.html",
            template: "src/templates/network_friends.html",
            chunks: ["friendAdd"],
            inject: false,
        }),
        new HtmlWebpackPlugin({
            filename: "templates/review.html",
            template: "src/templates/review.html",
            chunks: ["review"],
            inject: false,
        }),
        new HtmlWebpackPlugin({
            filename: "templates/auth/register.html",
            template: "src/templates/register.html",
            chunks: ["register"],
            inject: false,
        }),

    ],
    resolve: {
        alias: {
          'vue': 'vue/dist/vue.esm.js' // 'vue/dist/vue.common.js' for webpack 1
        }
    }

}