/// Tests for the INI-style configuration parser.
///
/// Covers:
/// - Parsing sections, key-value pairs, and comments
/// - Whitespace trimming behavior
/// - All public accessors: get(), keys(), sections()
/// - Error cases: malformed sections, empty keys, invalid lines
/// - Edge cases: empty input, duplicate keys/sections, values with '='
/// - Property-based test: parser never panics on arbitrary input

// Include the source under test
include!("config_parser.rs");

#[cfg(test)]
mod tests {
    use super::*;

    // -----------------------------------------------------------------------
    // Parsing: basic happy paths
    // -----------------------------------------------------------------------

    #[test]
    fn parse_single_section_with_key_value_pairs() {
        let input = "[database]\nhost = localhost\nport = 5432\nname = mydb";
        let config = Config::parse(input).expect("should parse successfully");

        assert_eq!(config.get("database", "host"), Some("localhost"));
        assert_eq!(config.get("database", "port"), Some("5432"));
        assert_eq!(config.get("database", "name"), Some("mydb"));
        assert_eq!(config.sections().len(), 1);
    }

    #[test]
    fn parse_multiple_sections() {
        let input = "\
[server]
host = 0.0.0.0
port = 8080

[logging]
level = debug
file = /var/log/app.log";

        let config = Config::parse(input).expect("should parse successfully");

        assert_eq!(config.get("server", "host"), Some("0.0.0.0"));
        assert_eq!(config.get("server", "port"), Some("8080"));
        assert_eq!(config.get("logging", "level"), Some("debug"));
        assert_eq!(config.get("logging", "file"), Some("/var/log/app.log"));

        let sections = config.sections();
        assert_eq!(sections.len(), 2);
        assert!(sections.contains(&"server"));
        assert!(sections.contains(&"logging"));
    }

    #[test]
    fn parse_comments_are_ignored() {
        let input = "\
# This is a comment
; This is also a comment
[section]
# another comment
key = value
; inline section comment
key2 = value2";

        let config = Config::parse(input).expect("should parse successfully");

        assert_eq!(config.get("section", "key"), Some("value"));
        assert_eq!(config.get("section", "key2"), Some("value2"));
        // Comments should not appear as keys or sections
        let keys = config.keys("section");
        assert_eq!(keys.len(), 2);
        assert!(keys.contains(&"key"));
        assert!(keys.contains(&"key2"));
    }

    #[test]
    fn parse_empty_lines_are_skipped() {
        let input = "\n\n[section]\n\nkey = value\n\n";
        let config = Config::parse(input).expect("should parse successfully");

        assert_eq!(config.get("section", "key"), Some("value"));
        assert_eq!(config.sections().len(), 1);
    }

    // -----------------------------------------------------------------------
    // Whitespace trimming
    // -----------------------------------------------------------------------

    #[test]
    fn whitespace_trimmed_from_keys_and_values() {
        let input = "[section]\n  key  =  value  ";
        let config = Config::parse(input).expect("should parse successfully");

        assert_eq!(config.get("section", "key"), Some("value"));
        // Verify the key is stored without surrounding whitespace
        let keys = config.keys("section");
        assert_eq!(keys.len(), 1);
        assert!(keys.contains(&"key"));
    }

    #[test]
    fn whitespace_trimmed_from_section_names() {
        let input = "[  my_section  ]\nkey = value";
        let config = Config::parse(input).expect("should parse successfully");

        assert_eq!(config.get("my_section", "key"), Some("value"));
        assert!(config.sections().contains(&"my_section"));
    }

    #[test]
    fn leading_whitespace_on_lines_is_trimmed() {
        let input = "   [section]\n   key = value";
        let config = Config::parse(input).expect("should parse successfully");

        assert_eq!(config.get("section", "key"), Some("value"));
    }

    // -----------------------------------------------------------------------
    // Key-value edge cases
    // -----------------------------------------------------------------------

    #[test]
    fn value_containing_equals_sign_preserves_everything_after_first_equals() {
        let input = "[math]\nequation = a = b + c";
        let config = Config::parse(input).expect("should parse successfully");

        // Only the first '=' splits key from value
        assert_eq!(config.get("math", "equation"), Some("a = b + c"));
    }

    #[test]
    fn empty_value_is_allowed() {
        let input = "[section]\nkey =";
        let config = Config::parse(input).expect("should parse successfully");

        assert_eq!(config.get("section", "key"), Some(""));
    }

    #[test]
    fn empty_value_with_trailing_spaces_trimmed_to_empty() {
        let input = "[section]\nkey =   ";
        let config = Config::parse(input).expect("should parse successfully");

        assert_eq!(config.get("section", "key"), Some(""));
    }

    #[test]
    fn key_value_before_any_section_stored_under_empty_string_section() {
        let input = "global_key = global_value\n[section]\nkey = value";
        let config = Config::parse(input).expect("should parse successfully");

        // Keys before any section header go into the "" section
        assert_eq!(config.get("", "global_key"), Some("global_value"));
        assert_eq!(config.get("section", "key"), Some("value"));
    }

    #[test]
    fn duplicate_key_in_same_section_last_value_wins() {
        let input = "[section]\nkey = first\nkey = second";
        let config = Config::parse(input).expect("should parse successfully");

        assert_eq!(config.get("section", "key"), Some("second"));
        // Only one key should exist
        assert_eq!(config.keys("section").len(), 1);
    }

    #[test]
    fn duplicate_section_headers_merge_into_same_section() {
        let input = "[section]\nkey1 = value1\n[section]\nkey2 = value2";
        let config = Config::parse(input).expect("should parse successfully");

        assert_eq!(config.get("section", "key1"), Some("value1"));
        assert_eq!(config.get("section", "key2"), Some("value2"));
        // Should still be treated as one section
        let keys = config.keys("section");
        assert!(keys.contains(&"key1"));
        assert!(keys.contains(&"key2"));
    }

    // -----------------------------------------------------------------------
    // Empty / minimal inputs
    // -----------------------------------------------------------------------

    #[test]
    fn parse_empty_string_produces_empty_config() {
        let config = Config::parse("").expect("should parse successfully");

        assert!(config.sections().is_empty());
        assert_eq!(config.get("any", "key"), None);
    }

    #[test]
    fn parse_only_comments_produces_empty_config() {
        let input = "# comment\n; another comment\n# more";
        let config = Config::parse(input).expect("should parse successfully");

        assert!(config.sections().is_empty());
    }

    #[test]
    fn parse_only_blank_lines_produces_empty_config() {
        let input = "\n\n   \n\n";
        let config = Config::parse(input).expect("should parse successfully");

        assert!(config.sections().is_empty());
    }

    #[test]
    fn section_with_no_keys() {
        let input = "[empty_section]";
        let config = Config::parse(input).expect("should parse successfully");

        assert!(config.sections().contains(&"empty_section"));
        assert!(config.keys("empty_section").is_empty());
        assert_eq!(config.get("empty_section", "anything"), None);
    }

    // -----------------------------------------------------------------------
    // Accessor methods: get(), keys(), sections()
    // -----------------------------------------------------------------------

    #[test]
    fn get_nonexistent_section_returns_none() {
        let input = "[section]\nkey = value";
        let config = Config::parse(input).expect("should parse successfully");

        assert_eq!(config.get("nonexistent", "key"), None);
    }

    #[test]
    fn get_nonexistent_key_returns_none() {
        let input = "[section]\nkey = value";
        let config = Config::parse(input).expect("should parse successfully");

        assert_eq!(config.get("section", "nonexistent"), None);
    }

    #[test]
    fn keys_for_nonexistent_section_returns_empty_vec() {
        let config = Config::parse("[section]\nkey = val").expect("should parse successfully");

        let keys = config.keys("no_such_section");
        assert!(keys.is_empty());
    }

    #[test]
    fn keys_returns_all_keys_in_section() {
        let input = "[section]\nalpha = 1\nbeta = 2\ngamma = 3";
        let config = Config::parse(input).expect("should parse successfully");

        let mut keys = config.keys("section");
        keys.sort();
        assert_eq!(keys, vec!["alpha", "beta", "gamma"]);
    }

    #[test]
    fn sections_returns_all_section_names() {
        let input = "[a]\nk=v\n[b]\nk=v\n[c]\nk=v";
        let config = Config::parse(input).expect("should parse successfully");

        let mut sections = config.sections();
        sections.sort();
        assert_eq!(sections, vec!["a", "b", "c"]);
    }

    // -----------------------------------------------------------------------
    // Config::new() and Default
    // -----------------------------------------------------------------------

    #[test]
    fn new_config_has_no_sections_and_returns_none_for_get() {
        let config = Config::new();

        assert!(config.sections().is_empty());
        assert_eq!(config.get("any", "key"), None);
        assert!(config.keys("any").is_empty());
    }

    #[test]
    fn default_config_behaves_same_as_new() {
        let config_new = Config::new();
        let config_default = Config::default();

        assert_eq!(config_new.sections().len(), config_default.sections().len());
        assert_eq!(config_new.get("x", "y"), config_default.get("x", "y"));
    }

    // -----------------------------------------------------------------------
    // Error cases
    // -----------------------------------------------------------------------

    #[test]
    fn error_missing_closing_bracket() {
        let input = "[section\nkey = value";
        let err = Config::parse(input).expect_err("should fail on missing bracket");

        assert_eq!(err.line, 1);
        assert!(
            err.message.contains("Missing closing bracket"),
            "expected 'Missing closing bracket' but got: {}",
            err.message
        );
    }

    #[test]
    fn error_empty_section_name() {
        let input = "[]\nkey = value";
        let err = Config::parse(input).expect_err("should fail on empty section name");

        assert_eq!(err.line, 1);
        assert!(
            err.message.contains("Empty section name"),
            "expected 'Empty section name' but got: {}",
            err.message
        );
    }

    #[test]
    fn error_whitespace_only_section_name_treated_as_empty() {
        let input = "[   ]\nkey = value";
        let err = Config::parse(input).expect_err("should fail on whitespace-only section name");

        assert_eq!(err.line, 1);
        assert!(
            err.message.contains("Empty section name"),
            "expected 'Empty section name' but got: {}",
            err.message
        );
    }

    #[test]
    fn error_empty_key() {
        let input = "[section]\n = value";
        let err = Config::parse(input).expect_err("should fail on empty key");

        assert_eq!(err.line, 2);
        assert!(
            err.message.contains("Empty key"),
            "expected 'Empty key' but got: {}",
            err.message
        );
    }

    #[test]
    fn error_line_without_equals_sign() {
        let input = "[section]\njust some text";
        let err = Config::parse(input).expect_err("should fail on line without '='");

        assert_eq!(err.line, 2);
        assert!(
            err.message.contains("Invalid line"),
            "expected 'Invalid line' but got: {}",
            err.message
        );
        // Error message should include the offending line content
        assert!(
            err.message.contains("just some text"),
            "error message should include the invalid line text"
        );
    }

    #[test]
    fn error_reports_correct_line_number_with_blank_lines_and_comments() {
        let input = "# comment\n\n\n[section]\n\ninvalid_line";
        let err = Config::parse(input).expect_err("should fail on invalid line");

        // Line 6 in the original input (1-indexed)
        assert_eq!(err.line, 6);
        assert!(err.message.contains("Invalid line"));
    }

    #[test]
    fn error_on_second_section_missing_bracket() {
        let input = "[valid]\nkey = value\n[invalid";
        let err = Config::parse(input).expect_err("should fail on malformed second section");

        assert_eq!(err.line, 3);
        assert!(err.message.contains("Missing closing bracket"));
    }

    // -----------------------------------------------------------------------
    // ParseError display and trait implementations
    // -----------------------------------------------------------------------

    #[test]
    fn parse_error_display_format() {
        let err = ParseError {
            line: 42,
            message: "Something went wrong".to_string(),
        };

        let display = format!("{}", err);
        assert_eq!(display, "Line 42: Something went wrong");
    }

    #[test]
    fn parse_error_implements_std_error() {
        let err = ParseError {
            line: 1,
            message: "test".to_string(),
        };
        // Verify it implements std::error::Error by using it as a trait object
        let _: &dyn std::error::Error = &err;
    }

    #[test]
    fn parse_error_is_debug() {
        let err = ParseError {
            line: 5,
            message: "oops".to_string(),
        };
        let debug_str = format!("{:?}", err);
        assert!(debug_str.contains("ParseError"));
        assert!(debug_str.contains("5"));
        assert!(debug_str.contains("oops"));
    }

    // -----------------------------------------------------------------------
    // Realistic configuration file
    // -----------------------------------------------------------------------

    #[test]
    fn parse_realistic_config_file() {
        let input = "\
; Application configuration
# Generated by setup wizard

[general]
app_name = My Application
version = 2.1.0
debug = false

[database]
host = db.example.com
port = 3306
username = admin
password = s3cr3t=pass=word

[logging]
level = info
file = /var/log/app.log
max_size = 10MB

[features]
enable_cache = true
enable_notifications = false
";

        let config = Config::parse(input).expect("should parse realistic config");

        // Verify all sections present
        let mut sections = config.sections();
        sections.sort();
        assert_eq!(sections, vec!["database", "features", "general", "logging"]);

        // Verify specific values across sections
        assert_eq!(config.get("general", "app_name"), Some("My Application"));
        assert_eq!(config.get("general", "debug"), Some("false"));
        assert_eq!(config.get("database", "host"), Some("db.example.com"));
        assert_eq!(config.get("database", "port"), Some("3306"));
        // Password contains '=' signs - only first '=' should split
        assert_eq!(
            config.get("database", "password"),
            Some("s3cr3t=pass=word")
        );
        assert_eq!(config.get("logging", "level"), Some("info"));
        assert_eq!(config.get("features", "enable_cache"), Some("true"));

        // Verify key counts
        assert_eq!(config.keys("general").len(), 3);
        assert_eq!(config.keys("database").len(), 4);
        assert_eq!(config.keys("logging").len(), 3);
        assert_eq!(config.keys("features").len(), 2);
    }

    // -----------------------------------------------------------------------
    // Config clone
    // -----------------------------------------------------------------------

    #[test]
    fn config_clone_is_independent() {
        let input = "[section]\nkey = value";
        let config = Config::parse(input).expect("should parse");
        let cloned = config.clone();

        // Cloned config has same data
        assert_eq!(cloned.get("section", "key"), Some("value"));
        assert_eq!(cloned.sections().len(), config.sections().len());
    }

    // -----------------------------------------------------------------------
    // Both comment styles work identically
    // -----------------------------------------------------------------------

    #[test]
    fn hash_and_semicolon_comments_both_ignored() {
        let hash_input = "# comment\n[section]\n# another\nkey = value";
        let semi_input = "; comment\n[section]\n; another\nkey = value";

        let hash_config = Config::parse(hash_input).expect("hash comments should parse");
        let semi_config = Config::parse(semi_input).expect("semicolon comments should parse");

        assert_eq!(hash_config.get("section", "key"), semi_config.get("section", "key"));
        assert_eq!(hash_config.sections().len(), semi_config.sections().len());
        assert_eq!(hash_config.keys("section").len(), semi_config.keys("section").len());
    }

    // -----------------------------------------------------------------------
    // Property-based: parser never panics on arbitrary input
    // -----------------------------------------------------------------------

    #[test]
    fn parser_never_panics_on_arbitrary_ascii_lines() {
        // A manual property-based-style test: feed various problematic strings
        // and ensure the parser either returns Ok or Err, but never panics.
        let inputs = vec![
            "",
            " ",
            "\n",
            "\n\n\n",
            "=",
            "= =",
            "==",
            "[",
            "]",
            "[]",
            "[[]]",
            "[section",
            "section]",
            "[ ]",
            "[  \t  ]",
            "key = value",
            "key=value",
            "key =",
            "= value",
            "===",
            "# comment",
            "; comment",
            "# [fake_section]",
            "; key = value",
            "[section]\n[section]",
            "[a]\nk=v\n[b]\nk=v\n[c]\nk=v",
            "\t\t[section]\t\t",
            "[section]\n\tkey\t=\tvalue\t",
            "no_section_key = val\n[s]\nk = v",
            "[s1]\nk = v\n\n\n[s2]\nk = v",
            &"x".repeat(10000),
            &format!("[{}]\nkey = value", "a".repeat(10000)),
            &format!("[section]\n{} = value", "k".repeat(10000)),
            &format!("[section]\nkey = {}", "v".repeat(10000)),
            "[section]\nk1=v\nk2=v\nk3=v\nk4=v\nk5=v\nk6=v\nk7=v\nk8=v\nk9=v\nk10=v",
            "[sect!@#$%^&*()]\nkey = value",
            "[section]\nkey with spaces = value with spaces",
            "[section]\nkey\twith\ttabs = value",
            "[a]\n[b]\n[c]\n[d]\n[e]",
            "\r\n[section]\r\nkey = value\r\n",
        ];

        for input in &inputs {
            // Must not panic - Ok or Err are both acceptable
            let _ = Config::parse(input);
        }
    }

    #[test]
    fn parser_handles_many_sections_without_panic() {
        let mut input = String::new();
        for i in 0..100 {
            input.push_str(&format!("[section_{}]\nkey_{} = value_{}\n", i, i, i));
        }
        let config = Config::parse(&input).expect("many sections should parse");
        assert_eq!(config.sections().len(), 100);
        assert_eq!(config.get("section_0", "key_0"), Some("value_0"));
        assert_eq!(config.get("section_99", "key_99"), Some("value_99"));
    }

    // -----------------------------------------------------------------------
    // Edge case: section bracket inside value
    // -----------------------------------------------------------------------

    #[test]
    fn bracket_in_value_does_not_start_new_section() {
        let input = "[section]\nkey = [not_a_section]";
        let config = Config::parse(input).expect("should parse");

        assert_eq!(config.get("section", "key"), Some("[not_a_section]"));
        assert_eq!(config.sections().len(), 1);
    }

    // -----------------------------------------------------------------------
    // Equals sign edge cases
    // -----------------------------------------------------------------------

    #[test]
    fn key_value_with_no_spaces_around_equals() {
        let input = "[section]\nkey=value";
        let config = Config::parse(input).expect("should parse");

        assert_eq!(config.get("section", "key"), Some("value"));
    }

    #[test]
    fn only_equals_sign_as_line_is_empty_key_error() {
        let input = "[section]\n=";
        let err = Config::parse(input).expect_err("bare '=' should fail with empty key");

        assert_eq!(err.line, 2);
        assert!(err.message.contains("Empty key"));
    }
}
