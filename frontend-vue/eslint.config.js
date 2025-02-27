import pluginVue from 'eslint-plugin-vue'
import js from '@eslint/js'
import process from 'process'

export default [
  js.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['**/*.{js,jsx,mjs,cjs,vue}'],
    rules: {
      'vue/multi-word-component-names': 'warn',
      'vue/no-unused-vars': 'error',
      'vue/script-setup-uses-vars': 'error',
      'vue/no-mutating-props': 'error',
      'vue/component-api-style': ['error', ['script-setup', 'composition']],
      'vue/block-order': ['error', {
        order: ['script', 'template', 'style']
      }],
      'vue/component-name-in-template-casing': ['error', 'PascalCase'],
      'vue/html-closing-bracket-newline': ['error', {
        singleline: 'never',
        multiline: 'never'
      }],
      'vue/max-attributes-per-line': ['error', {
        singleline: {
          max: 4,
        },
        multiline: {
          max: 1,
        }
      }],
      'vue/html-indent': ['error', 2],
      'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'warn',
      'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'warn'
    }
  }
]
