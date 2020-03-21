'use strict';

// Here's a JavaScript-based config file.
// If you need conditional logic, you might want to use this type of config.
// Otherwise, JSON or YAML is recommended.

module.exports = {
  require: ['esm'],
  diff: true,
  extension: ['js'],
  file: 'app/frontend/test/setup.js',
  recursive: true,
  package: 'app/frontend/package.json',
  reporter: 'spec',
  slow: 75,
  timeout: 3000,
  ui: 'bdd',
  'watch-files': ['app/frontend/test/**/*.js'],
};