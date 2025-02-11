<?php

namespace App\Entity;

use App\Repository\RawScrapedDataRepository;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: RawScrapedDataRepository::class)]
#[ORM\Table(name: "raw_scraped_datas")]
class RawScrapedData
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(length: 500)]
    private ?string $source_url = null;

    #[ORM\Column(type: Types::TEXT)]
    private ?string $raw_data = null;

    #[ORM\Column]
    private ?\DateTimeImmutable $scraped_at = null;

    #[ORM\Column(type: "boolean", options: ["default" => false])]
    private ?bool $processed = null;

    #[ORM\Column(type: Types::TEXT, nullable: true)]
    private ?string $error_message = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getSourceUrl(): ?string
    {
        return $this->source_url;
    }

    public function setSourceUrl(string $source_url): static
    {
        $this->source_url = $source_url;

        return $this;
    }

    public function getRawData(): ?string
    {
        return $this->raw_data;
    }

    public function setRawData(string $raw_data): static
    {
        $this->raw_data = $raw_data;

        return $this;
    }

    public function getScrapedAt(): ?\DateTimeImmutable
    {
        return $this->scraped_at;
    }

    public function setScrapedAt(\DateTimeImmutable $scraped_at): static
    {
        $this->scraped_at = $scraped_at;

        return $this;
    }

    public function isProcessed(): ?bool
    {
        return $this->processed;
    }

    public function setProcessed(bool $processed): static
    {
        $this->processed = $processed;

        return $this;
    }

    public function getErrorMessage(): ?string
    {
        return $this->error_message;
    }

    public function setErrorMessage(?string $error_message): static
    {
        $this->error_message = $error_message;

        return $this;
    }
}
