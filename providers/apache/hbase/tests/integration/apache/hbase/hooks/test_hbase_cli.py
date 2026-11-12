#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

import os

import pytest

from airflow.models import Connection
from airflow.providers.apache.hbase.hooks.hbase_cli import HBaseCLIHook

CONN_ID = "hbase_cli_test"
HBASE_HOST = os.environ.get(
    "HBASE_HOST", "hbase" if os.environ.get("INTEGRATION_HBASE") == "true" else "localhost"
)
HBASE_HOME = os.environ.get("HBASE_HOME", "/opt/hbase")
JAVA_HOME_8 = os.environ.get("JAVA_HOME_8", "/usr/lib/jvm/temurin-8-jdk-amd64")
JAVA_HOME_DEFAULT = os.environ.get("JAVA_HOME", "/usr/lib/jvm/temurin-17-jdk-amd64")


@pytest.mark.integration("hbase")
class TestHBaseCLIHookIntegration:
    def setup_method(self):
        os.environ["AIRFLOW_CONN_HBASE_CLI_TEST"] = Connection(
            conn_id=CONN_ID,
            conn_type="hbase",
            host=HBASE_HOST,
            port=9090,
            extra={"java_home": JAVA_HOME_DEFAULT, "hbase_home": HBASE_HOME},
        ).as_json()

    def test_java_home_from_extra_is_used(self):
        """Test that java_home from Extra is applied when executing hbase command."""
        hook = HBaseCLIHook(hbase_conn_id=CONN_ID, java_home=JAVA_HOME_8)
        _, env = hook._prepare_command(["version"])
        assert env["JAVA_HOME"] == JAVA_HOME_DEFAULT

    def test_java_home_fallback_to_constructor_when_not_in_extra(self):
        """Test that java_home falls back to constructor value when not in Extra."""
        os.environ["AIRFLOW_CONN_HBASE_CLI_TEST"] = Connection(
            conn_id=CONN_ID,
            conn_type="hbase",
            host=HBASE_HOST,
            port=9090,
        ).as_json()
        hook = HBaseCLIHook(hbase_conn_id=CONN_ID, java_home=JAVA_HOME_8)
        _, env = hook._prepare_command(["version"])
        assert env["JAVA_HOME"] == JAVA_HOME_8

    def test_hbase_home_from_extra_is_used(self):
        """Test that hbase_home from Extra is applied to env and binary path."""
        hook = HBaseCLIHook(hbase_conn_id=CONN_ID, hbase_home="/fallback/hbase")
        cmd, env = hook._prepare_command(["version"])
        assert env["HBASE_HOME"] == HBASE_HOME
        assert cmd[0] == f"{HBASE_HOME}/bin/hbase"

    def test_hbase_home_fallback_to_constructor_when_not_in_extra(self):
        """Test that hbase_home falls back to constructor value when not in Extra."""
        os.environ["AIRFLOW_CONN_HBASE_CLI_TEST"] = Connection(
            conn_id=CONN_ID,
            conn_type="hbase",
            host=HBASE_HOST,
            port=9090,
        ).as_json()
        hook = HBaseCLIHook(hbase_conn_id=CONN_ID, hbase_home="/fallback/hbase")
        cmd, env = hook._prepare_command(["version"])
        assert env["HBASE_HOME"] == "/fallback/hbase"
        assert cmd[0] == "/fallback/hbase/bin/hbase"
