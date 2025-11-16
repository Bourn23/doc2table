### Troubleshooting

# ❌ Frontend shows "Failed to load resource: 404" or "405 Method Not Allowed"

**Problem**: Frontend can't reach the backend API.

**Solution**:
```bash
./manage-lumina.sh
# Select Option 13: Fix Frontend Issues
# Then select Option 5: Fix All Issues
```

This will:
1. Update `.env.production` with correct backend URL
2. Rebuild the frontend
3. Redeploy to S3

#### ❌ Backend services not starting

**Problem**: Docker containers fail to start or crash immediately.

**Solution**: Check the logs:
```bash
./manage-lumina.sh
# Select Option 12: View Docker Logs
```

Common causes:
- **Missing API keys**: Edit `.env` file and add `NVIDIA_API_KEY` and `GOOGLE_GEMINI_API_KEY`
- **Port conflicts**: Another service is using ports 8000, 8001, or 8002
- **Docker build failed**: Check if you have enough disk space

**Fix**:
```bash
# SSH to instance
ssh -i <your-key>.pem ec2-user@<your-ip>

# Edit .env file
nano .env

# Add your API keys, then restart
docker compose -f docker-compose-backend.yml restart
```

#### ❌ "No columns could be queried successfully"

**Problem**: Query service can't find indexes created by extraction service.

**Cause**: Services aren't sharing the `indexed_volume` properly.

**Solution**: Redeploy with the latest code (this was fixed):
```bash
./manage-lumina.sh
# Select Option 8: Redeploy Backend Code
```

#### ❌ "Index 'column_education_history' not found"

**Problem**: Dynamically extracted columns can't be queried.

**Cause**: Column name sanitization mismatch between services.

**Solution**: This was fixed in the latest version. Redeploy:
```bash
./manage-lumina.sh
# Select Option 8: Redeploy Backend Code
```

#### ❌ Frontend shows `[object Object]` in table cells

**Problem**: Nested objects/arrays not displaying correctly.

**Solution**: This was fixed in the latest version. Redeploy frontend:
```bash
./manage-lumina.sh
# Select Option 9: Redeploy Frontend
```

#### ❌ "Request failed with status code 500"

**Problem**: Backend error during processing.

**Solution**: Check backend logs for details:
```bash
./manage-lumina.sh
# Select Option 12: View Docker Logs
# Select Option 2: View specific container logs
# Enter: api-service (or extraction-service, or query-service)
```

Common causes:
- Invalid API keys
- LLM API rate limits exceeded
- Database connection issues

#### ❌ EC2 instance IP changed after restart

**Problem**: After stopping/starting EC2, the public IP changes.

**Solution**: The frontend needs to be updated with the new IP:
```bash
# The new IP is automatically saved to backend-instance-personal.env
# Just redeploy the frontend:
./manage-lumina.sh
# Select Option 9: Redeploy Frontend
```

#### 💡 General Debugging Tips

1. **Check system status first**:
   ```bash
   ./manage-lumina.sh
   # Select Option 4: Show System Status
   ```

2. **Test endpoints**:
   ```bash
   ./manage-lumina.sh
   # Select Option 10: Test Endpoints
   ```

3. **View deployment info**:
   ```bash
   ./manage-lumina.sh
   # Select Option 11: Show Deployment Info
   ```

4. **SSH to instance for manual debugging**:
   ```bash
   ssh -i <your-key>.pem ec2-user@<your-ip>
   
   # Check container status
   docker ps
   
   # View logs
   docker logs api-service
   docker logs extraction-service
   docker logs query-service
   
   # Check disk space
   df -h
   
   # Check memory
   free -h
   ```