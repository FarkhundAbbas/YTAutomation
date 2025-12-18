            "ipv4": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
            "timestamp_iso": r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?",
            "timestamp_common": r"\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}",
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "username": r"\b[a-zA-Z][a-zA-Z0-9_-]{2,31}\b",
            "number": r"\b\d+\b",
            "word": r"\b\w+\b",
            "severity": r"\b(DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|FATAL)\b",
            "uuid": r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
        }
    
    def analyze_logs(self, logs: List[str]) -> Dict[str, Any]:
        """Analyze log patterns to identify structure."""
        if not logs:
            return {}
        
        # Find common tokens
        all_tokens = []
        for log in logs[:100]:  # Sample first 100
            tokens = re.findall(r'\S+', log)
            all_tokens.extend(tokens)
        
        token_freq = Counter(all_tokens)
        common_tokens = {k: v for k, v in token_freq.items() if v > len(logs) * 0.5}
        
        # Detect common patterns
        pattern_matches = {}
        for name, pattern in self.common_patterns.items():
            matches = []
            for log in logs[:10]:
                found = re.findall(pattern, log)
                if found:
                    matches.extend(found)
            if matches:
                pattern_matches[name] = matches[:5]
        
        return {
            "log_count": len(logs),
            "average_length": sum(len(log) for log in logs) / len(logs),
            "common_tokens": list(common_tokens.keys())[:10],
            "detected_patterns": pattern_matches
        }
    
    def generate_regex_patterns(self, logs: List[str]) -> List[Dict[str, Any]]:
        """Generate regex patterns from sample logs."""
        if not logs:
            return []
        
        analysis = self.analyze_logs(logs)
        candidates = []
        
        # Strategy 1: Template-based extraction
        pattern1 = self._generate_template_pattern(logs)
        if pattern1:
            candidates.append({
                "pattern": pattern1,
                "pattern_type": "regex",
                "explanation": "Template-based pattern using common log structures",
                "confidence": 0.85,
                "synthetic_tests": self._generate_synthetic_logs(pattern1, 3)
            })
        
        # Strategy 2: Field-based extraction
        pattern2 = self._generate_field_pattern(logs, analysis)
        if pattern2:
            candidates.append({
                "pattern": pattern2,
                "pattern_type": "regex",
                "explanation": "Field-based extraction focusing on key-value pairs",
                "confidence": 0.75,
                "synthetic_tests": self._generate_synthetic_logs(pattern2, 3)
            })
        
            r'(?P<ip>\\b(?:[0-9]{1,3}\\.){3}[0-9]{1,3}\\b)',
            pattern
        )
        
        # Timestamps
        pattern = re.sub(
            r'\d{4}[-/]\d{2}[-/]\d{2}[T ]\d{2}:\d{2}:\d{2}',
            r'(?P<timestamp>\\d{4}[-/]\\d{2}[-/]\\d{2}[T ]\\d{2}:\\d{2}:\\d{2})',
            pattern
        )
        
        # Numbers
        pattern = re.sub(r'\b\d+\b', r'(?P<number>\\d+)', pattern)
        
        # Usernames (common patterns)
        pattern = re.sub(
            r'\buser[=:]?\s*(\w+)',
            r'user[=:]?\\s*(?P<username>\\w+)',
            pattern,
            flags=re.IGNORECASE
        )
        
        return pattern
    
    def _generate_field_pattern(self, logs: List[str], analysis: Dict[str, Any]) -> str:
        """Generate field-based regex pattern."""
        # Look for key=value or key:value patterns
        pattern_parts = []
        
        if "ipv4" in analysis.get("detected_patterns", {}):
            pattern_parts.append(r'(?:ip|addr)[:=]\s*(?P<ip>(?:[0-9]{1,3}\.){3}[0-9]{1,3})')
        
        if "username" in analysis.get("detected_patterns", {}):
            pattern_parts.append(r'(?:user|username)[:=]\s*(?P<user>\w+)')
        
        pattern_parts.append(r'(?P<message>.*)')
        
        return r'\s*'.join(pattern_parts) if pattern_parts else ""
    
    def _generate_grok_pattern(self, logs: List[str], analysis: Dict[str, Any]) -> str:
        """Generate grok-style pattern."""
        grok_parts = []
        
        if "timestamp_iso" in analysis.get("detected_patterns", {}) or \
           "timestamp_common" in analysis.get("detected_patterns", {}):
            grok_parts.append("%{TIMESTAMP:timestamp}")
        
        if "severity" in analysis.get("detected_patterns", {}):
            grok_parts.append("%{LOGLEVEL:level}")
        
        if "ipv4" in analysis.get("detected_patterns", {}):
            grok_parts.append(".*(?:from|ip)[=:]?%{IP:ip}")
        
        grok_parts.append("%{GREEDYDATA:message}")
        
        return " ".join(grok_parts) if grok_parts else "%{GREEDYDATA:message}"
    
    def _generate_synthetic_logs(self, pattern: str, count: int) -> List[str]:
        """Generate synthetic test logs based on pattern."""
        # Simplified synthetic generation
        return [
            "2025-01-01T12:00:00Z host app - - Failed login for user john from 10.0.0.1",
            "2025-01-02T13:30:00Z host app - - Failed login for user jane from 10.0.0.2",
            "2025-01-03T14:45:00Z host app - - Failed login for user bob from 10.0.0.3",
        ][:count]
    
    def generate_platform_decoder(
        self,
        platform: str,
        pattern: str,
        pattern_type: str
    ) -> Dict[str, Any]:
        """Generate platform-specific decoder configuration."""
        if platform == "elastic":
            return self._generate_elastic_pipeline(pattern, pattern_type)
        elif platform == "wazuh":
            return self._generate_wazuh_decoder(pattern, pattern_type)
        elif platform == "splunk":
            return self._generate_splunk_config(pattern, pattern_type)
        elif platform == "qradar":
            return self._generate_qradar_dsm(pattern, pattern_type)
        else:
            return {}
    
    def _generate_elastic_pipeline(self, pattern: str, pattern_type: str) -> Dict[str, Any]:
        """Generate Elasticsearch ingest pipeline."""
        processors = []
        
        if pattern_type == "grok":
            processors.append({
                "grok": {
                    "field": "message",
                    "patterns": [pattern],
                    "ignore_failure": True
                }
            })
        else:
            # Use dissect for simpler patterns
            processors.append({
                "dissect": {
                    "field": "message",
                    "pattern": pattern,
                    "ignore_failure": True
                }
            })
        
        processors.append({
            "date": {
                "field": "timestamp",
                "target_field": "@timestamp",
                "formats": ["ISO8601", "yyyy/MM/dd HH:mm:ss"],
                "ignore_failure": True
            }
        })
        
        return {
            "pipeline": {
                "description": "AI Log Doctor generated pipeline",
                "processors": processors
            }
        }
    
    def _generate_wazuh_decoder(self, pattern: str, pattern_type: str) -> Dict[str, Any]:
        """Generate Wazuh XML decoder."""
        decoder_xml = f"""<decoder name="logdoctor_custom">
  <program_name>^.*$</program_name>
  <regex>{pattern}</regex>
  <order>timestamp, user, ip, message</order>
</decoder>"""
        
        return {
            "decoder_xml": decoder_xml,
            "decoder_file": "logdoctor_decoder.xml"
        }
    
    def _generate_splunk_config(self, pattern: str, pattern_type: str) -> Dict[str, Any]:
        """Generate Splunk props.conf and transforms.conf."""
        props_conf = """[custom:logdoctor]
SHOULD_LINEMERGE = false
TIME_PREFIX = ^
TIME_FORMAT = %Y-%m-%dT%H:%M:%S
MAX_TIMESTAMP_LOOKAHEAD = 25
TRANSFORMS-extract = logdoctor_extract
"""
        
        transforms_conf = f"""[logdoctor_extract]
REGEX = {pattern}
FORMAT = ip::$1 user::$2 message::$3
"""
        
        return {
            "props_conf": props_conf,
            "transforms_conf": transforms_conf,
            "sourcetype": "custom:logdoctor"
        }
    
    def _generate_qradar_dsm(self, pattern: str, pattern_type: str) -> Dict[str, Any]:
        """Generate QRadar DSM configuration."""
        return {
            "dsm_name": "LogDoctor Custom DSM",
            "dsm_config": {
                "event_mappings": [
                    {
                        "regex": pattern,
                        "fields": ["timestamp", "user", "ip", "message"]
                    }
                ]
            }
        }


# Singleton instance
inference_engine = InferenceEngine()
