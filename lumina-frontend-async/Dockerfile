# --- STAGE 1: Build the React App ---
# Use an official Node.js image to build the app
FROM node:18-alpine AS build

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of your app's source code
COPY . .

# Build the app for production
RUN npm run build

# --- STAGE 2: Serve the App with Nginx ---
# Use a lightweight Nginx image
FROM nginx:1.27-alpine

# Copy the static build files from the 'build' stage
COPY --from=build /app/dist /usr/share/nginx/html

# We will add a custom Nginx configuration file next
# For now, remove the default Nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy your new Nginx config (we'll create this in Step 2)
COPY nginx.conf /etc/nginx/conf.d

# Expose port 80
EXPOSE 80
