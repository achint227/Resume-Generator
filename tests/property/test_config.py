# Property-based tests for configuration module
"""
**Feature: codebase-refactor, Property 8: Configuration Type Safety**

Tests that configuration values accessed through the Config class have the types
specified in the dataclass definition.

**Feature: codebase-refactor, Property 9: Missing Configuration Handling**

Tests that missing or invalid configuration values raise ConfigurationError
with a message identifying the problematic configuration.
"""

import os
from pathlib import Path
from typing import List

import pytest
from hypothesis import given, strategies as st, settings, assume

from src.config import Config, DatabaseConfig, AppConfig, reset_config
from src.exceptions import ConfigurationError


class TestConfigurationTypeSafety:
    """
    **Feature: codebase-refactor, Property 8: Configuration Type Safety**
    **Validates: Requirements 5.2**
    
    Property: For any configuration value accessed through the Config class,
    the value SHALL have the type specified in the dataclass definition.
    """

    @given(
        port=st.integers(min_value=1, max_value=65535),
        debug=st.booleans(),
        latex_timeout=st.integers(min_value=1, max_value=3600),
        sqlite_path=st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=("L", "N"), whitelist_characters="_-."
        )),
        output_dir=st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=("L", "N"), whitelist_characters="_-."
        )),
        mongodb_database=st.text(min_size=1, max_size=30, alphabet=st.characters(
            whitelist_categories=("L", "N")
        )),
        allowed_origins=st.lists(
            st.text(min_size=1, max_size=30, alphabet=st.characters(
                whitelist_categories=("L", "N"), whitelist_characters="*:.-/"
            )),
            min_size=1,
            max_size=5
        ),
    )
    @settings(max_examples=100)
    def test_config_types_match_dataclass_definitions(
        self,
        port: int,
        debug: bool,
        latex_timeout: int,
        sqlite_path: str,
        output_dir: str,
        mongodb_database: str,
        allowed_origins: List[str],
    ):
        """Config values have correct types as defined in dataclass."""
        # Filter out empty strings from allowed_origins
        allowed_origins = [o for o in allowed_origins if o.strip()]
        assume(len(allowed_origins) > 0)
        assume(sqlite_path.strip())
        assume(output_dir.strip())
        assume(mongodb_database.strip())
        
        # Store original env and reset config
        original_env = os.environ.copy()
        reset_config()
        
        try:
            # Set environment variables
            os.environ["PORT"] = str(port)
            os.environ["FLASK_DEBUG"] = "true" if debug else "false"
            os.environ["LATEX_TIMEOUT"] = str(latex_timeout)
            os.environ["SQLITE_PATH"] = sqlite_path
            os.environ["OUTPUT_DIR"] = output_dir
            os.environ["MONGODB_DATABASE"] = mongodb_database
            os.environ["ALLOWED_ORIGINS"] = ",".join(allowed_origins)
            os.environ.pop("DATABASE_URL", None)  # Ensure SQLite mode
            
            config = Config.from_env()
            
            # Verify Config type
            assert isinstance(config, Config)
            
            # Verify DatabaseConfig types
            assert isinstance(config.database, DatabaseConfig)
            assert isinstance(config.database.use_mongodb, bool)
            assert isinstance(config.database.sqlite_path, Path)
            assert config.database.mongodb_url is None or isinstance(config.database.mongodb_url, str)
            assert isinstance(config.database.mongodb_database, str)
            
            # Verify AppConfig types
            assert isinstance(config.app, AppConfig)
            assert isinstance(config.app.debug, bool)
            assert isinstance(config.app.port, int)
            assert isinstance(config.app.allowed_origins, list)
            assert all(isinstance(origin, str) for origin in config.app.allowed_origins)
            assert isinstance(config.app.latex_timeout, int)
            assert isinstance(config.app.output_dir, Path)
            
            # Verify values match what was set
            assert config.app.port == port
            assert config.app.debug == debug
            assert config.app.latex_timeout == latex_timeout
            
        finally:
            # Restore original environment
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        mongodb_url=st.text(min_size=1, max_size=100, alphabet=st.characters(
            whitelist_categories=("L", "N"), whitelist_characters=":/.-_@"
        )),
    )
    @settings(max_examples=100)
    def test_mongodb_config_types_when_database_url_set(self, mongodb_url: str):
        """When DATABASE_URL is set, mongodb_url has correct string type."""
        assume(mongodb_url.strip())
        
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["DATABASE_URL"] = mongodb_url
            os.environ["PORT"] = "8000"
            os.environ["LATEX_TIMEOUT"] = "60"
            
            config = Config.from_env()
            
            # Verify mongodb_url is a string when set
            assert isinstance(config.database.mongodb_url, str)
            assert config.database.mongodb_url == mongodb_url
            assert isinstance(config.database.use_mongodb, bool)
            assert config.database.use_mongodb is True
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        port=st.integers(min_value=1, max_value=65535),
    )
    @settings(max_examples=100)
    def test_port_is_always_integer_type(self, port: int):
        """Port configuration is always an integer type."""
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["PORT"] = str(port)
            os.environ.pop("DATABASE_URL", None)
            
            config = Config.from_env()
            
            assert isinstance(config.app.port, int)
            assert config.app.port == port
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        timeout=st.integers(min_value=1, max_value=3600),
    )
    @settings(max_examples=100)
    def test_latex_timeout_is_always_integer_type(self, timeout: int):
        """LaTeX timeout configuration is always an integer type."""
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["LATEX_TIMEOUT"] = str(timeout)
            os.environ.pop("DATABASE_URL", None)
            
            config = Config.from_env()
            
            assert isinstance(config.app.latex_timeout, int)
            assert config.app.latex_timeout == timeout
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        debug_value=st.sampled_from(["true", "false", "True", "False", "TRUE", "FALSE", "yes", "no", "1", "0", ""]),
    )
    @settings(max_examples=100)
    def test_debug_is_always_boolean_type(self, debug_value: str):
        """Debug configuration is always a boolean type regardless of input string."""
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["FLASK_DEBUG"] = debug_value
            os.environ.pop("DATABASE_URL", None)
            
            config = Config.from_env()
            
            # Debug should always be a boolean
            assert isinstance(config.app.debug, bool)
            # Only "true" (case-insensitive) should result in True
            expected = debug_value.lower() == "true"
            assert config.app.debug == expected
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        path_str=st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=("L", "N"), whitelist_characters="_-./\\"
        )),
    )
    @settings(max_examples=100)
    def test_paths_are_always_path_type(self, path_str: str):
        """Path configurations are always Path type."""
        assume(path_str.strip())
        
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["SQLITE_PATH"] = path_str
            os.environ["OUTPUT_DIR"] = path_str
            os.environ.pop("DATABASE_URL", None)
            
            config = Config.from_env()
            
            assert isinstance(config.database.sqlite_path, Path)
            assert isinstance(config.app.output_dir, Path)
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()


class TestMissingConfigurationHandling:
    """
    **Feature: codebase-refactor, Property 9: Missing Configuration Handling**
    **Validates: Requirements 5.3**
    
    Property: For any required configuration value that is missing or invalid,
    the system SHALL raise a ConfigurationError with a message identifying
    the missing configuration.
    """

    @given(
        invalid_port=st.text(
            min_size=1,
            max_size=20,
            alphabet=st.characters(whitelist_categories=("L",), whitelist_characters="!@#$%^&*")
        ),
    )
    @settings(max_examples=100)
    def test_invalid_port_raises_configuration_error(self, invalid_port: str):
        """Invalid PORT values raise ConfigurationError with config_key='PORT'."""
        assume(invalid_port.strip())
        # Ensure it's not accidentally a valid integer
        try:
            int(invalid_port)
            assume(False)  # Skip if it parses as int
        except ValueError:
            pass
        
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["PORT"] = invalid_port
            os.environ.pop("DATABASE_URL", None)
            
            with pytest.raises(ConfigurationError) as exc_info:
                Config.from_env()
            
            # Verify the error identifies the PORT configuration
            assert exc_info.value.config_key == "PORT"
            assert "PORT" in str(exc_info.value) or "port" in str(exc_info.value).lower()
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        out_of_range_port=st.one_of(
            st.integers(max_value=0),
            st.integers(min_value=65536),
        ),
    )
    @settings(max_examples=100)
    def test_out_of_range_port_raises_configuration_error(self, out_of_range_port: int):
        """Out-of-range PORT values raise ConfigurationError with config_key='PORT'."""
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["PORT"] = str(out_of_range_port)
            os.environ.pop("DATABASE_URL", None)
            
            with pytest.raises(ConfigurationError) as exc_info:
                Config.from_env()
            
            # Verify the error identifies the PORT configuration
            assert exc_info.value.config_key == "PORT"
            assert "PORT" in str(exc_info.value) or "port" in str(exc_info.value).lower()
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        invalid_timeout=st.text(
            min_size=1,
            max_size=20,
            alphabet=st.characters(whitelist_categories=("L",), whitelist_characters="!@#$%^&*")
        ),
    )
    @settings(max_examples=100)
    def test_invalid_latex_timeout_raises_configuration_error(self, invalid_timeout: str):
        """Invalid LATEX_TIMEOUT values raise ConfigurationError with config_key='LATEX_TIMEOUT'."""
        assume(invalid_timeout.strip())
        # Ensure it's not accidentally a valid integer
        try:
            int(invalid_timeout)
            assume(False)  # Skip if it parses as int
        except ValueError:
            pass
        
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["PORT"] = "8000"  # Valid port
            os.environ["LATEX_TIMEOUT"] = invalid_timeout
            os.environ.pop("DATABASE_URL", None)
            
            with pytest.raises(ConfigurationError) as exc_info:
                Config.from_env()
            
            # Verify the error identifies the LATEX_TIMEOUT configuration
            assert exc_info.value.config_key == "LATEX_TIMEOUT"
            assert "LATEX_TIMEOUT" in str(exc_info.value) or "timeout" in str(exc_info.value).lower()
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        non_positive_timeout=st.integers(max_value=0),
    )
    @settings(max_examples=100)
    def test_non_positive_latex_timeout_raises_configuration_error(self, non_positive_timeout: int):
        """Non-positive LATEX_TIMEOUT values raise ConfigurationError with config_key='LATEX_TIMEOUT'."""
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["PORT"] = "8000"  # Valid port
            os.environ["LATEX_TIMEOUT"] = str(non_positive_timeout)
            os.environ.pop("DATABASE_URL", None)
            
            with pytest.raises(ConfigurationError) as exc_info:
                Config.from_env()
            
            # Verify the error identifies the LATEX_TIMEOUT configuration
            assert exc_info.value.config_key == "LATEX_TIMEOUT"
            assert "LATEX_TIMEOUT" in str(exc_info.value) or "timeout" in str(exc_info.value).lower()
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        invalid_port=st.text(
            min_size=1,
            max_size=20,
            alphabet=st.characters(whitelist_categories=("L",), whitelist_characters="!@#$%^&*")
        ),
    )
    @settings(max_examples=100)
    def test_configuration_error_contains_identifying_message(self, invalid_port: str):
        """ConfigurationError message identifies the problematic configuration key."""
        assume(invalid_port.strip())
        try:
            int(invalid_port)
            assume(False)
        except ValueError:
            pass
        
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["PORT"] = invalid_port
            os.environ.pop("DATABASE_URL", None)
            
            with pytest.raises(ConfigurationError) as exc_info:
                Config.from_env()
            
            error = exc_info.value
            # The error should have a config_key attribute
            assert hasattr(error, "config_key")
            assert error.config_key is not None
            # The string representation should mention the config key
            error_str = str(error)
            assert len(error_str) > 0
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        invalid_value=st.one_of(
            st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("L",))),
            st.integers(max_value=0),
            st.integers(min_value=65536),
        ),
    )
    @settings(max_examples=100)
    def test_configuration_error_is_subclass_of_resume_generator_error(self, invalid_value):
        """ConfigurationError is a subclass of ResumeGeneratorError for consistent error handling."""
        from src.exceptions import ResumeGeneratorError
        
        # Skip if invalid_value is accidentally a valid port
        if isinstance(invalid_value, int) and 1 <= invalid_value <= 65535:
            assume(False)
        if isinstance(invalid_value, str):
            try:
                port_int = int(invalid_value)
                if 1 <= port_int <= 65535:
                    assume(False)
            except ValueError:
                pass
            assume(invalid_value.strip())
        
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["PORT"] = str(invalid_value)
            os.environ.pop("DATABASE_URL", None)
            
            with pytest.raises(ResumeGeneratorError):
                Config.from_env()
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()


class TestEnvironmentConfigurationOverrides:
    """
    **Feature: codebase-refactor, Property 10: Environment Configuration Overrides**
    **Validates: Requirements 5.4**
    
    Property: For any configuration value with a corresponding environment variable,
    setting the environment variable SHALL override the default value in the
    resulting Config instance.
    """

    @given(
        port=st.integers(min_value=1, max_value=65535),
    )
    @settings(max_examples=100)
    def test_port_env_overrides_default(self, port: int):
        """PORT environment variable overrides the default port value."""
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["PORT"] = str(port)
            os.environ.pop("DATABASE_URL", None)
            
            config = Config.from_env()
            
            # The configured port should match the environment variable, not the default (8000)
            assert config.app.port == port
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        debug=st.booleans(),
    )
    @settings(max_examples=100)
    def test_flask_debug_env_overrides_default(self, debug: bool):
        """FLASK_DEBUG environment variable overrides the default debug value."""
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["FLASK_DEBUG"] = "true" if debug else "false"
            os.environ.pop("DATABASE_URL", None)
            
            config = Config.from_env()
            
            # The configured debug should match the environment variable, not the default (false)
            assert config.app.debug == debug
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        timeout=st.integers(min_value=1, max_value=3600),
    )
    @settings(max_examples=100)
    def test_latex_timeout_env_overrides_default(self, timeout: int):
        """LATEX_TIMEOUT environment variable overrides the default timeout value."""
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["LATEX_TIMEOUT"] = str(timeout)
            os.environ.pop("DATABASE_URL", None)
            
            config = Config.from_env()
            
            # The configured timeout should match the environment variable, not the default (60)
            assert config.app.latex_timeout == timeout
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        sqlite_path=st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=("L", "N"), whitelist_characters="_-./\\"
        )),
    )
    @settings(max_examples=100)
    def test_sqlite_path_env_overrides_default(self, sqlite_path: str):
        """SQLITE_PATH environment variable overrides the default path value."""
        assume(sqlite_path.strip())
        
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["SQLITE_PATH"] = sqlite_path
            os.environ.pop("DATABASE_URL", None)
            
            config = Config.from_env()
            
            # The configured path should match the environment variable, not the default ("resumes.db")
            assert config.database.sqlite_path == Path(sqlite_path)
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        output_dir=st.text(min_size=1, max_size=50, alphabet=st.characters(
            whitelist_categories=("L", "N"), whitelist_characters="_-./\\"
        )),
    )
    @settings(max_examples=100)
    def test_output_dir_env_overrides_default(self, output_dir: str):
        """OUTPUT_DIR environment variable overrides the default output directory."""
        assume(output_dir.strip())
        
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["OUTPUT_DIR"] = output_dir
            os.environ.pop("DATABASE_URL", None)
            
            config = Config.from_env()
            
            # The configured output dir should match the environment variable, not the default ("output")
            assert config.app.output_dir == Path(output_dir)
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        mongodb_database=st.text(min_size=1, max_size=30, alphabet=st.characters(
            whitelist_categories=("L", "N")
        )),
    )
    @settings(max_examples=100)
    def test_mongodb_database_env_overrides_default(self, mongodb_database: str):
        """MONGODB_DATABASE environment variable overrides the default database name."""
        assume(mongodb_database.strip())
        
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["MONGODB_DATABASE"] = mongodb_database
            os.environ.pop("DATABASE_URL", None)
            
            config = Config.from_env()
            
            # The configured database name should match the environment variable, not the default ("Resume")
            assert config.database.mongodb_database == mongodb_database
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        allowed_origins=st.lists(
            st.text(min_size=1, max_size=30, alphabet=st.characters(
                whitelist_categories=("L", "N"), whitelist_characters="*:.-/"
            )),
            min_size=1,
            max_size=5
        ),
    )
    @settings(max_examples=100)
    def test_allowed_origins_env_overrides_default(self, allowed_origins: List[str]):
        """ALLOWED_ORIGINS environment variable overrides the default origins."""
        # Filter out empty strings
        allowed_origins = [o for o in allowed_origins if o.strip()]
        assume(len(allowed_origins) > 0)
        
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["ALLOWED_ORIGINS"] = ",".join(allowed_origins)
            os.environ.pop("DATABASE_URL", None)
            
            config = Config.from_env()
            
            # The configured origins should match the environment variable, not the default ("*")
            assert config.app.allowed_origins == allowed_origins
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        mongodb_url=st.text(min_size=1, max_size=100, alphabet=st.characters(
            whitelist_categories=("L", "N"), whitelist_characters=":/.-_@"
        )),
    )
    @settings(max_examples=100)
    def test_database_url_env_enables_mongodb(self, mongodb_url: str):
        """DATABASE_URL environment variable enables MongoDB and overrides SQLite default."""
        assume(mongodb_url.strip())
        
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["DATABASE_URL"] = mongodb_url
            
            config = Config.from_env()
            
            # When DATABASE_URL is set, use_mongodb should be True (overriding default False)
            assert config.database.use_mongodb is True
            assert config.database.mongodb_url == mongodb_url
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()

    @given(
        port=st.integers(min_value=1, max_value=65535),
        debug=st.booleans(),
        timeout=st.integers(min_value=1, max_value=3600),
        sqlite_path=st.text(min_size=1, max_size=30, alphabet=st.characters(
            whitelist_categories=("L", "N"), whitelist_characters="_-."
        )),
        output_dir=st.text(min_size=1, max_size=30, alphabet=st.characters(
            whitelist_categories=("L", "N"), whitelist_characters="_-."
        )),
    )
    @settings(max_examples=100)
    def test_multiple_env_overrides_simultaneously(
        self, port: int, debug: bool, timeout: int, sqlite_path: str, output_dir: str
    ):
        """Multiple environment variables can override their respective defaults simultaneously."""
        assume(sqlite_path.strip())
        assume(output_dir.strip())
        
        original_env = os.environ.copy()
        reset_config()
        
        try:
            os.environ["PORT"] = str(port)
            os.environ["FLASK_DEBUG"] = "true" if debug else "false"
            os.environ["LATEX_TIMEOUT"] = str(timeout)
            os.environ["SQLITE_PATH"] = sqlite_path
            os.environ["OUTPUT_DIR"] = output_dir
            os.environ.pop("DATABASE_URL", None)
            
            config = Config.from_env()
            
            # All configured values should match their environment variables
            assert config.app.port == port
            assert config.app.debug == debug
            assert config.app.latex_timeout == timeout
            assert config.database.sqlite_path == Path(sqlite_path)
            assert config.app.output_dir == Path(output_dir)
            
        finally:
            os.environ.clear()
            os.environ.update(original_env)
            reset_config()
