@Library('libpipelines') _

hose {
    EMAIL = 'genai'
    DEVTIMEOUT = 60
    RELEASETIMEOUT = 60
    BUILDTOOL = 'make'
    BUILDTOOL_IMAGE = 'stratio/python-builder-3.9:1.0.0'
    BUILDTOOL_CPU_LIMIT = '8'
    BUILDTOOL_CPU_REQUEST = '2'
    PYTHON_MODULE = true
    GRYPE_TEST = false
    LABEL_CONTROL = true
    DEPLOYONPRS = true

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
                "sonar.python.coverage.reportPaths": "basic-actor-chain-example/pytest-coverage.xml,virtualizer-chain-example/pytest-coverage.xml,opensearch-chain-example/pytest-coverage.xml,memory-chain-example/pytest-coverage.xml",
                "sonar.python.pylint.reportPaths": "basic-actor-chain-example/pylint-report.txt,virtualizer-chain-example/pylint-report.txt,opensearch-chain-example/pylint-report.txt,memory-chain-example/pylint-report.txt",
                "sonar.scm.disabled": "true"
            ]
        )
        doPackage(config)
        doDeploy(config)
    }
}
