/// A simple INI-style configuration parser.
///
/// Supports:
/// - Sections: [section_name]
/// - Key-value pairs: key = value
/// - Comments: lines starting with # or ;
/// - Whitespace trimming on keys and values

use std::collections::HashMap;

#[derive(Debug, Clone, Default)]
pub struct Config {
    sections: HashMap<String, HashMap<String, String>>,
}

impl Config {
    pub fn new() -> Self {
        Config {
            sections: HashMap::new(),
        }
    }

    /// Parse an INI string into a Config.
    pub fn parse(input: &str) -> Result<Config, ParseError> {
        let mut config = Config::new();
        let mut current_section = String::new();

        for (line_num, line) in input.lines().enumerate() {
            let trimmed = line.trim();

            // Skip empty lines and comments
            if trimmed.is_empty() || trimmed.starts_with('#') || trimmed.starts_with(';') {
                continue;
            }

            // Section header
            if trimmed.starts_with('[') {
                if !trimmed.ends_with(']') {
                    return Err(ParseError {
                        line: line_num + 1,
                        message: "Missing closing bracket".to_string(),
                    });
                }
                current_section = trimmed[1..trimmed.len() - 1].trim().to_string();
                if current_section.is_empty() {
                    return Err(ParseError {
                        line: line_num + 1,
                        message: "Empty section name".to_string(),
                    });
                }
                config
                    .sections
                    .entry(current_section.clone())
                    .or_insert_with(HashMap::new);
                continue;
            }

            // Key-value pair
            if let Some(eq_pos) = trimmed.find('=') {
                let key = trimmed[..eq_pos].trim().to_string();
                let value = trimmed[eq_pos + 1..].trim().to_string();
                if key.is_empty() {
                    return Err(ParseError {
                        line: line_num + 1,
                        message: "Empty key".to_string(),
                    });
                }
                config
                    .sections
                    .entry(current_section.clone())
                    .or_insert_with(HashMap::new)
                    .insert(key, value);
            } else {
                return Err(ParseError {
                    line: line_num + 1,
                    message: format!("Invalid line: {}", trimmed),
                });
            }
        }

        Ok(config)
    }

    /// Get a value from a section.
    pub fn get(&self, section: &str, key: &str) -> Option<&str> {
        self.sections
            .get(section)
            .and_then(|s| s.get(key))
            .map(|s| s.as_str())
    }

    /// Get all keys in a section.
    pub fn keys(&self, section: &str) -> Vec<&str> {
        self.sections
            .get(section)
            .map(|s| s.keys().map(|k| k.as_str()).collect())
            .unwrap_or_default()
    }

    /// Get all section names.
    pub fn sections(&self) -> Vec<&str> {
        self.sections.keys().map(|k| k.as_str()).collect()
    }
}

#[derive(Debug)]
pub struct ParseError {
    pub line: usize,
    pub message: String,
}

impl std::fmt::Display for ParseError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "Line {}: {}", self.line, self.message)
    }
}

impl std::error::Error for ParseError {}
