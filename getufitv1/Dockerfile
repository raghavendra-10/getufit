# Use the official Node.js 18 image as the base
FROM node:18-alpine

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the Next.js application
RUN npm run build

# Expose the port (optional, Cloud Run uses the PORT environment variable)
EXPOSE 8080

# Start the Next.js application
CMD ["npm", "start"]
