#!/bin/bash
dbt docs generate --project-dir fund_accounting --profiles-dir ./ && dbt docs serve --project-dir fund_accounting --profiles-dir ./ --port 8888
