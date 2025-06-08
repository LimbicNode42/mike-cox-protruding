"""
InfluxDB database manager and operations
"""

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.query_api import QueryApi
from typing import Optional, List, Dict, Any
import logging
import asyncio

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

    async def connect(self):
        """Connect to InfluxDB"""
        try:
            # Run synchronous client creation in executor to make it async-compatible
            loop = asyncio.get_event_loop()
            self.client = await loop.run_in_executor(
                None,
                lambda: InfluxDBClient(url=self.url, token=self.token, org=self.org),
            )

            # Test connection with ready check
            ready = await loop.run_in_executor(None, self.client.ready)
            if ready.status == "ready":
                logger.info(f"Connected to InfluxDB at {self.url}")
            else:
                raise Exception(f"InfluxDB ready check failed: {ready.status}")
        except Exception as e:
            logger.error(f"Failed to connect to InfluxDB: {e}")
            raise

    async def disconnect(self):
        """Disconnect from InfluxDB"""
        if self.client:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.client.close)
            self.client = None

    async def get_buckets(self) -> List[Dict[str, Any]]:
        """Get list of buckets"""
        if not self.client:
            raise ConnectionError("Not connected to InfluxDB")

        try:
            loop = asyncio.get_event_loop()
            buckets_api = self.client.buckets_api()
            buckets = await loop.run_in_executor(None, buckets_api.find_buckets)

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

    async def get_measurements(self, bucket: str, start_time: str = "-1h") -> List[str]:
        """Get list of measurements (similar to tables) in a bucket"""
        if not self.client:
            raise ConnectionError("Not connected to InfluxDB")

        try:
            loop = asyncio.get_event_loop()
            query_api = self.client.query_api()

            # Query to get unique measurements
            flux_query = f"""
            import "influxdata/influxdb/schema"
            schema.measurements(bucket: "{bucket}")
            """

            result = await loop.run_in_executor(
                None, query_api.query, flux_query, self.org
            )
            measurements = []

            for table in result:
                for record in table.records:
                    if hasattr(record, "get_value") and record.get_value():
                        measurements.append(record.get_value())

            return list(set(measurements))  # Remove duplicates
        except Exception as e:
            # Fallback method if schema.measurements doesn't work
            try:
                fallback_query = f"""
                from(bucket: "{bucket}")
                    |> range(start: {start_time})
                    |> keep(columns: ["_measurement"])
                    |> distinct(column: "_measurement")
                """
                loop = asyncio.get_event_loop()
                query_api = self.client.query_api()
                result = await loop.run_in_executor(
                    None, query_api.query, fallback_query, self.org
                )

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

    async def get_fields(
        self, bucket: str, measurement: str, start_time: str = "-1h"
    ) -> List[Dict[str, Any]]:
        """Get list of fields for a measurement"""
        if not self.client:
            raise ConnectionError("Not connected to InfluxDB")

        try:
            loop = asyncio.get_event_loop()
            query_api = self.client.query_api()

            flux_query = f"""
            from(bucket: "{bucket}")
                |> range(start: {start_time})
                |> filter(fn: (r) => r._measurement == "{measurement}")
                |> keep(columns: ["_field", "_value"])
                |> distinct(column: "_field")
            """

            result = await loop.run_in_executor(
                None, query_api.query, flux_query, self.org
            )
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

    async def get_tags(
        self, bucket: str, measurement: str, start_time: str = "-1h"
    ) -> List[Dict[str, Any]]:
        """Get list of tag keys for a measurement"""
        if not self.client:
            raise ConnectionError("Not connected to InfluxDB")

        try:
            loop = asyncio.get_event_loop()
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

            result = await loop.run_in_executor(
                None, query_api.query, flux_query, self.org
            )
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

    async def get_tag_values(
        self, bucket: str, measurement: str, tag_key: str, start_time: str = "-1h"
    ) -> List[str]:
        """Get values for a specific tag key"""
        if not self.client:
            raise ConnectionError("Not connected to InfluxDB")

        try:
            loop = asyncio.get_event_loop()
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

            result = await loop.run_in_executor(
                None, query_api.query, flux_query, self.org
            )
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

    async def query_data(self, bucket: str, flux_query: str) -> List[Dict[str, Any]]:
        """Execute a Flux query and return results"""
        if not self.client:
            raise ConnectionError("Not connected to InfluxDB")

        try:
            loop = asyncio.get_event_loop()
            query_api = self.client.query_api()

            # If the query doesn't specify a bucket, add it
            if (
                f'from(bucket: "{bucket}")' not in flux_query
                and "from(bucket:" not in flux_query
            ):
                flux_query = f'from(bucket: "{bucket}")\\n' + flux_query

            result = await loop.run_in_executor(
                None, query_api.query, flux_query, self.org
            )

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

    async def get_sample_data(
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

        return await self.query_data(bucket, flux_query)

    async def get_server_info(self) -> Dict[str, Any]:
        """Get InfluxDB server information"""
        if not self.client:
            raise ConnectionError("Not connected to InfluxDB")

        try:
            loop = asyncio.get_event_loop()
            ready = await loop.run_in_executor(None, self.client.ready)

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
