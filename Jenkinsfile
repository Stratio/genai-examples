@Library('libpipelines') _

hose {
    EMAIL = 'genai'
    DEVTIMEOUT = 60
    RELEASETIMEOUT = 60
    BUILDTOOL = 'make'
    BUILDTOOL_IMAGE = 'stratio/python-builder-3.9:1.1.1'
    BUILDTOOL_CPU_LIMIT = '8'
    BUILDTOOL_CPU_REQUEST = '2'
    PYTHON_MODULE = true
    GRYPE_TEST = false
    LABEL_CONTROL = true
    DEPLOYONPRS = false

    DEV = { config ->
        doCompile(config)
        doUT(config)
        doStaticAnalysis(
            conf: config,
            sonarAdditionalProperties: [
                "sonar.language": "py",
                "sonar.python.version": "3.9",
                "sonar.sources": ".",
                "sonar.exclusions": "*/tests/**,*/scripts/**,*/pytest-coverage.xml",
                "sonar.tests": ".",
                "sonar.test.inclusions": "*/tests/**",
                "sonar.python.coverage.reportPaths": "example-chain-basic-actor/pytest-coverage.xml,example-chain-chat-memory/pytest-coverage.xml,example-chain-opensearch/pytest-coverage.xml,example-chain-virtualizer/pytest-coverage.xml",
                "sonar.python.pylint.reportPaths": "example-chain-basic-actor/pylint-report.txt,example-chain-chat-memory/pylint-report.txt,example-chain-opensearch/pylint-report.txt,example-chain-virtualizer/pylint-report.txt",
                "sonar.scm.disabled": "true"
            ]
        )
    }
}
