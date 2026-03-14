<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

final class Version20260308000000 extends AbstractMigration
{
    public function getDescription(): string
    {
        return 'Change status_text column from VARCHAR(50) to JSON to support multiple statuses';
    }

    public function up(Schema $schema): void
    {
        // 先にカラム型を拡張してから JSON 配列化（VARCHAR(50) のまま UPDATE すると文字数増で切り捨てリスクがあるため）
        $this->addSql('ALTER TABLE operations CHANGE status_text status_text LONGTEXT DEFAULT NULL COMMENT \'(DC2Type:json)\'');
        $this->addSql("UPDATE operations SET status_text = JSON_ARRAY(status_text) WHERE status_text IS NOT NULL AND JSON_VALID(status_text) = 0");
    }

    public function down(Schema $schema): void
    {
        $this->addSql('ALTER TABLE operations CHANGE status_text status_text LONGTEXT DEFAULT NULL');
    }
}
