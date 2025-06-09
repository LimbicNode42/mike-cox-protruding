"""
InfluxDB database manager and operations
"""

import logging
from typing import Any, Dict, List, Optional

from influxdb_client import InfluxDBClient

logger = logging.getLogger(__name__)


class InfluxDBManager:
    """InfluxDB connection and operations manager"""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 8086,
        token: Optional[str] = None,
        org: Optional[str] = None,
        bucket: Optional[str] = None,
    ):
        self.host = host
        self.port = port
        self.token = token
        self.org = org
        self.bucket = bucket
        self.url = f"http://{host}:{port}"
        self.client: Optional[InfluxDBClient] = None

    def connect(self):
        """Connect to InfluxDB"""
        try:
            self.client = InfluxDBClient(url=self.url, token=self.token, org=self.org)

            # Test connection with ready check
            ready = self.client.ready()
            if ready.status == "ready":
                logger.info(f"Connected to InfluxDB at {self.url}")
            else:
                raise Exception(f"InfluxDB ready check failed: {ready.status}")
        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
            raise

    def disconnect(self):
        """Disconnect from InfluxDB"""
        if self.client:
            self.client.close()
            self.client = None

    def get_buckets(self) -> List[Dict[str, Any]]:
        """Get list of buckets"""
        if not self.client:
            raise ConnectionError("Not connected to InfluxDB")

        try:
            buckets_api = self.client.buckets_api()
            buckets = buckets_api.find_buckets()

            bucket_list = []
            for bucket in buckets:
                bucket_list.append(
                    {
                        "id": bucket.id,
                        "name": bucket.name,
                        "org_id": bucket.org_id,
                        "retention_rules": [
                            {
                                "type": rule.type,
                                "every_seconds": rule.every_seconds
                                if hasattr(rule, "every_seconds")
                                else None,
                            }
                            for rule in bucket.retention_rules
                        ]
                        if bucket.retention_rules
                        else [],
                        "created_at": bucket.created_at.isoformat()
                        if bucket.created_at
                        else None,
                        "updated_at": bucket.updated_at.isoformat()
                        if bucket.updated_at
                        else None,
                    }
                )

            return bucket_list
        except Exception as e:
            logger.warning(f"Failed to query buckets: {e}")
            # Return the configured bucket as fallback
            return [
                {
                    "id": "unknown",
                    "name": self.bucket or "default",
                    "org_id": "unknown",
                    "retention_rules": [],
                    "created_at": None,
                    "updated_at": None,
                }
            ]

    def get_measurements(self, bucket: str, start_time: str = "-1h") -> List[str]:
        """Get list of measurements (similar to tables) in a bucket"""
        if not self.client:
            raise ConnectionError("Not connected to InfluxDB")

        try:
            query_api = self.client.query_api()

            # Query to get unique measurements
            flux_query = f"""
            import "influxdata/influxdb/schema"
            schema.measurements(bucket: "{bucket}")
            """

            result = query_api.query(flux_query, self.org)
            measurements = []

            for table in result:
                for record in table.records:
                    if hasattr(record, "get_value") and record.get_value():
                        measurements.append(record.get_value())

            return list(set(measurements))  # Remove duplicates
        except Exception:
            # Fallback method if schema.measurements doesn't work
            try:
                fallback_query = f"""
                from(bucket: "{bucket}")
                    |> range(start: {start_time})
                    |> keep(columns: ["_measurement"])
                    |> distinct(column: "_measurement")
                """
                query_api = self.client.query_api()
                result = query_api.query(fallback_query, self.org)

                measurements = []
                for table in result:
                    for record in table.records:
                        measurement = record.get_value()
                        if measurement:
                            measurements.append(measurement)
                return list(set(measurements))
            except Exception as fallback_e:
                logger.warning(
                    f"Failed to get measurements with fallback: {fallback_e}"
                )
                return []

    def get_fields(
        self, bucket: str, measurement: str, start_time: str = "-1h"
    ) -> List[Dict[str, Any]]:
        """Get list of fields for a measurement"""
        if not self.client:
            raise ConnectionError("Not connected to InfluxDB")

        try:
            query_api = self.client.query_api()

            flux_query = f"""
            from(bucket: "{bucket}")
                |> range(start: {start_time})
                |> filter(fn: (r) => r._measurement == "{measurement}")
                |> keep(columns: ["_field", "_value"])
                |> distinct(column: "_field")
            """

            result = query_api.query(flux_query, self.org)
            fields = []

            for table in result:
                for record in table.records:
                    field_name = record.get_value()
                    if field_name:
                        fields.append({"field": field_name})

            return fields
        except Exception as e:
            logger.warning(f"Failed to get fields: {e}")
            return []

    def get_tags(
        self, bucket: str, measurement: str, start_time: str = "-1h"
    ) -> List[Dict[str, Any]]:
        """Get list of tag keys for a measurement"""
        if not self.client:
            raise ConnectionError("Not connected to InfluxDB")

        try:
            query_api = self.client.query_api()

            # Get tag keys using schema.tagKeys
            flux_query = f"""
            import "influxdata/influxdb/schema"
            schema.tagKeys(
                bucket: "{bucket}",
                predicate: (r) => r._measurement == "{measurement}",
                start: {start_time}
            )
            """

            result = query_api.query(flux_query, self.org)
            tags = []

            for table in result:
                for record in table.records:
                    tag_key = record.get_value()
                    if tag_key:
                        tags.append({"tag_key": tag_key})

            return tags
        except Exception as e:
            logger.warning(f"Failed to get tags: {e}")
            return []

    def get_tag_values(
        self, bucket: str, measurement: str, tag_key: str, start_time: str = "-1h"
    ) -> List[str]:
        """Get values for a specific tag key"""
        if not self.client:
            raise ConnectionError("Not connected to InfluxDB")

        try:
            query_api = self.client.query_api()

            flux_query = f"""
            import "influxdata/influxdb/schema"
            schema.tagValues(
                bucket: "{bucket}",
                tag: "{tag_key}",
                predicate: (r) => r._measurement == "{measurement}",
                start: {start_time}
            )
            """

            result = query_api.query(flux_query, self.org)
            values = []

            for table in result:
                for record in table.records:
                    value = record.get_value()
                    if value:
                        values.append(value)

            return values
        except Exception as e:
            logger.warning(f"Failed to get tag values: {e}")
            return []

    def query_data(self, bucket: str, flux_query: str) -> List[Dict[str, Any]]:
        """Execute a Flux query and return results"""
        if not self.client:
            raise ConnectionError("Not connected to InfluxDB")

        try:
            query_api = self.client.query_api()

            # If the query doesn't specify a bucket, add it
            if (
                f'from(bucket: "{bucket}")' not in flux_query
                and "from(bucket:" not in flux_query
            ):
                flux_query = f'from(bucket: "{bucket}")\\n' + flux_query

            result = query_api.query(flux_query, self.org)

            data = []
            for table in result:
                for record in table.records:
                    row = {
                        "time": record.get_time().isoformat()
                        if record.get_time()
                        else None,
                        "measurement": record.get_measurement(),
                        "field": record.get_field(),
                        "value": record.get_value(),
                    }

                    # Add tag values
                    if hasattr(record, "values") and record.values:
                        for key, value in record.values.items():
                            if key.startswith("_") and key not in [
                                "_time",
                                "_measurement",
                                "_field",
                                "_value",
                            ]:
                                continue
                            if not key.startswith("_"):
                                row[f"tag_{key}"] = value

                    data.append(row)

            return data
        except Exception as e:
            logger.error(f"Failed to execute query: {e}")
            raise

    def get_sample_data(
        self, bucket: str, measurement: str, limit: int = 10, start_time: str = "-1h"
    ) -> List[Dict[str, Any]]:
        """Get sample data from a measurement"""
        if not self.client:
            raise ConnectionError("Not connected to InfluxDB")

        flux_query = f"""
        from(bucket: "{bucket}")
            |> range(start: {start_time})
            |> filter(fn: (r) => r._measurement == "{measurement}")
            |> limit(n: {limit})
        """

        return self.query_data(bucket, flux_query)

    def get_server_info(self) -> Dict[str, Any]:
        """Get InfluxDB server information"""
        if not self.client:
            raise ConnectionError("Not connected to InfluxDB")

        try:
            ready = self.client.ready()

            return {
                "status": ready.status if ready else "unknown",
                "ready": ready.status if ready else "unknown",
                "url": self.url,
                "org": self.org,
                "bucket": self.bucket,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "url": self.url,
                "org": self.org,
                "bucket": self.bucket,
            }
