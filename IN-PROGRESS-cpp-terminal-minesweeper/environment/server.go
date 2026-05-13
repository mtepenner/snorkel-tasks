package main

import (
	"github.com/gin-gonic/gin"
	"net/http"
)

func main() {
	r := gin.Default()
	r.GET("/board", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "ok", "mines": 10, "board_state": "hidden"})
	})
	r.POST("/move", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "cleared"})
	})
	r.Run(":8080")
}
