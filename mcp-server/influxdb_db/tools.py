"""
InfluxDB tools for the MCP server
"""

from mcp.server.fastmcp import FastMCP
import json


def register_influxdb_tools(mcp: FastMCP):
    """Register InfluxDB-related tools with the MCP server"""

    @mcp.tool()
    async def influxdb_query(bucket: str, flux_query: str) -> str:
        """Execute a Flux query on InfluxDB"""
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager

        if influxdb_manager is None:
            return "InfluxDB is disabled. Please enable it in configuration to use this tool."

        try:
            results = await influxdb_manager.query_data(bucket, flux_query)
            return (
                f"InfluxDB query results: {json.dumps(results, indent=2, default=str)}"
            )
        except Exception as e:
            return f"Failed to execute InfluxDB query: {str(e)}" @ mcp.tool()

    async def influxdb_write_data(
        bucket: str, measurement: str, tags: str, fields: str, timestamp: str = ""
    ) -> str:
        """Write data to InfluxDB using line protocol format

        Args:
            bucket: Target bucket name
            measurement: Measurement name
            tags: Tags in JSON format (e.g., '{"host": "server1", "region": "us-west"}')
            fields: Fields in JSON format (e.g., '{"temperature": 23.5, "humidity": 45.2}')
            timestamp: Optional timestamp (ISO format), uses current time if empty
        """
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager

        if influxdb_manager is None:
            return "InfluxDB is disabled. Please enable it in configuration to use this tool."

        try:
            # Parse tags and fields from JSON
            import json
            from datetime import datetime

            tag_dict = json.loads(tags) if tags else {}
            field_dict = json.loads(fields)

            # Build line protocol format
            tag_string = ",".join([f"{k}={v}" for k, v in tag_dict.items()])
            field_string = ",".join([f"{k}={v}" for k, v in field_dict.items()])

            if tag_string:
                line_protocol = f"{measurement},{tag_string} {field_string}"
            else:
                line_protocol = f"{measurement} {field_string}"

            if timestamp:
                line_protocol += f" {timestamp}"

            # Access InfluxDB client through manager
            client = influxdb_manager.client
            write_api = client.write_api()
            write_api.write(bucket=bucket, record=line_protocol)
            write_api.close()

            return f"Data written successfully to InfluxDB bucket '{bucket}': {line_protocol}"
        except Exception as e:
            return f"Failed to write data to InfluxDB: {str(e)}" @ mcp.tool()

    async def influxdb_create_bucket(
        bucket_name: str, retention_period: str = "30d"
    ) -> str:
        """Create a new bucket in InfluxDB

        Args:
            bucket_name: Name of the bucket to create
            retention_period: Data retention period (e.g., "30d", "1h", "infinite")
        """
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager

        if influxdb_manager is None:
            return "InfluxDB is disabled. Please enable it in configuration to use this tool."

        try:
            # Access InfluxDB client through manager
            client = influxdb_manager.client
            buckets_api = client.buckets_api()

            # Create bucket with retention policy
            org = influxdb_manager.org
            bucket = buckets_api.create_bucket(
                bucket_name=bucket_name,
                org=org,
                retention_rules=[
                    {
                        "type": "expire",
                        "everySeconds": self._parse_retention_period(retention_period),
                    }
                ],
            )

            return f"Bucket '{bucket_name}' created successfully with retention period '{retention_period}'"
        except Exception as e:
            return (
                f"Failed to create InfluxDB bucket '{bucket_name}': {str(e)}"
                @ mcp.tool()
            )

    async def influxdb_delete_data(
        bucket: str, start_time: str, end_time: str, predicate: str = ""
    ) -> str:
        """Delete data from InfluxDB bucket

        Args:
            bucket: Target bucket name
            start_time: Start time (RFC3339 format, e.g., "2023-01-01T00:00:00Z")
            end_time: End time (RFC3339 format, e.g., "2023-01-02T00:00:00Z")
            predicate: Optional delete predicate (e.g., '_measurement="temperature"')
        """
        ctx = mcp.get_context()
        influxdb_manager = ctx.request_context.lifespan_context.influxdb_manager

        if influxdb_manager is None:
            return "InfluxDB is disabled. Please enable it in configuration to use this tool."

        try:
            # Access InfluxDB client through manager
            client = influxdb_manager.client
            delete_api = client.delete_api()

            delete_api.delete(
                start_time, end_time, predicate, bucket=bucket, org=influxdb_manager.org
            )

            return f"Data deleted successfully from bucket '{bucket}' between {start_time} and {end_time}"
        except Exception as e:
            return f"Failed to delete data from InfluxDB: {str(e)}"
