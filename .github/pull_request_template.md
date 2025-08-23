name: Pull Request / 拉取请求
description: Contribute code or documentation to TungShing / 向 TungShing 贡献代码或文档

body:
  - type: markdown
    attributes:
      value: |
        Thank you for contributing to TungShing! / 感谢您为 TungShing 做出贡献！
        
        Please fill out this template to help us review your changes.
        请填写此模板以帮助我们审查您的更改。

  - type: textarea
    id: description
    attributes:
      label: Description / 描述
      description: Briefly describe what this PR does / 简要描述此 PR 的作用
      placeholder: This PR adds/fixes/improves...
    validations:
      required: true

  - type: textarea
    id: motivation
    attributes:
      label: Motivation and Context / 动机和上下文
      description: Why is this change required? What problem does it solve? / 为什么需要这个更改？它解决了什么问题？
      placeholder: This change is needed because...
    validations:
      required: true

  - type: checkboxes
    id: type
    attributes:
      label: Type of Change / 更改类型
      description: What type of change does this PR introduce? / 此 PR 引入了什么类型的更改？
      options:
        - label: Bug fix / 错误修复
        - label: New feature / 新功能
        - label: Breaking change / 破坏性更改
        - label: Documentation update / 文档更新
        - label: Performance improvement / 性能改进
        - label: Code refactoring / 代码重构
        - label: Test addition/improvement / 测试添加/改进

  - type: textarea
    id: testing
    attributes:
      label: Testing / 测试
      description: How has this been tested? Please describe the tests that you ran / 这是如何测试的？请描述您运行的测试
      placeholder: |
        - [ ] Unit tests pass
        - [ ] Integration tests pass
        - [ ] Manual testing performed
    validations:
      required: true

  - type: checkboxes
    id: checklist
    attributes:
      label: Checklist / 检查清单
      description: Please check all that apply / 请勾选所有适用的选项
      options:
        - label: My code follows the style guidelines of this project / 我的代码遵循此项目的样式指南
        - label: I have performed a self-review of my own code / 我已对自己的代码进行了自我审查
        - label: I have commented my code, particularly in hard-to-understand areas / 我已对代码进行注释，特别是在难以理解的区域
        - label: I have made corresponding changes to the documentation / 我已对文档进行了相应的更改
        - label: My changes generate no new warnings / 我的更改不会产生新的警告
        - label: I have added tests that prove my fix is effective or that my feature works / 我已添加证明我的修复有效或我的功能正常工作的测试
        - label: New and existing unit tests pass locally with my changes / 新的和现有的单元测试在我的更改下本地通过
        - label: Any dependent changes have been merged and published in downstream modules / 任何依赖更改都已在下游模块中合并和发布

  - type: textarea
    id: additional
    attributes:
      label: Additional Notes / 附加说明
      description: Any additional information that would be helpful / 任何有用的附加信息
    validations:
      required: false